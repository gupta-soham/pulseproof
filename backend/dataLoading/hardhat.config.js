import "@nomicfoundation/hardhat-ethers";
import dotenv from "dotenv";

dotenv.config();

/** @type import('hardhat/config').HardhatUserConfig */
const config = {
  solidity: "0.8.17",
  networks: {
    hardhat: {
      type: "edr-simulated"
    },
    // Add your network configurations here when you have RPC URLs
    ...("https://eth-sepolia.g.alchemy.com/v2/x8JVZqgY9secV0Uz_0pUx" ? {
      sepolia: {
        type: "http",
        url: "https://eth-sepolia.g.alchemy.com/v2/x8JVZqgY9secV0Uz_0pUx",
        accounts: process.env.PRIVATE_KEY !== undefined ? [process.env.PRIVATE_KEY] : [],
      }
    } : {}),
    ...(process.env.MAINNET_URL ? {
      mainnet: {
        type: "http", 
        url: process.env.MAINNET_URL,
        accounts: process.env.PRIVATE_KEY !== undefined ? [process.env.PRIVATE_KEY] : [],
      }
    } : {}),
    polygon: {
      type: "http",
      url: process.env.POLYGON_URL || "https://polygon-rpc.com/",
      accounts: process.env.PRIVATE_KEY !== undefined ? [process.env.PRIVATE_KEY] : [],
    },
  },
};

export default config;