// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Referência acadêmica — contrato inspirado na implementação open-source do Drex
// Fonte: https://github.com/pedrosgmagalhaes/drex_smartcontracts

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    event Transfer(address indexed from, address indexed to, uint256 value);
}

contract DrexToken is IERC20 {
    string public constant name = "Drex";
    string public constant symbol = "DREX";
    uint8 public constant decimals = 2;

    address public owner; // Banco Central do Brasil
    uint256 private _totalSupply;

    mapping(address => uint256) private _balances;
    mapping(address => bool) public frozen;

    event Mint(address indexed to, uint256 amount);
    event Burn(address indexed from, uint256 amount);
    event Freeze(address indexed account, bool status);

    modifier onlyOwner() {
        require(msg.sender == owner, "Apenas o BCB pode executar");
        _;
    }

    modifier notFrozen(address account) {
        require(!frozen[account], "Conta congelada");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function totalSupply() external view override returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) external view override returns (uint256) {
        return _balances[account];
    }

    // Apenas BCB pode emitir (atacado)
    function mint(address to, uint256 amount) external onlyOwner notFrozen(to) {
        _totalSupply += amount;
        _balances[to] += amount;
        emit Mint(to, amount);
        emit Transfer(address(0), to, amount);
    }

    // Queima reduz oferta monetária
    function burn(uint256 amount) external notFrozen(msg.sender) {
        require(_balances[msg.sender] >= amount, "Saldo insuficiente");
        _balances[msg.sender] -= amount;
        _totalSupply -= amount;
        emit Burn(msg.sender, amount);
        emit Transfer(msg.sender, address(0), amount);
    }

    // Controle regulatório do BCB
    function freeze(address account, bool status) external onlyOwner {
        frozen[account] = status;
        emit Freeze(account, status);
    }

    function transfer(address to, uint256 amount)
        external
        override
        notFrozen(msg.sender)
        notFrozen(to)
        returns (bool)
    {
        require(_balances[msg.sender] >= amount, "Saldo insuficiente");
        _balances[msg.sender] -= amount;
        _balances[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }
}
