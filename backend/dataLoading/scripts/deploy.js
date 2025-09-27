import { ethers } from "ethers";
import fs from "fs";
import path from "path";

async function main() {
  console.log("Deploying PoCRegistry contract...");

  // Read the contract artifact
  const artifactPath = path.join(process.cwd(), "artifacts/contracts/PoCRegistry.sol/PoCRegistry.json");
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

  // Create provider and wallet for local deployment
  const provider = new ethers.JsonRpcProvider("https://eth-sepolia.g.alchemy.com/v2/x8JVZqgY9secV0Uz_0pUx");
  
  // Use first account from local node or private key from env
  let wallet;
  if ("46b63544ad6af04884b846a536926f2efee06d7f154c3b2366bbbaf277266d9f") {
    wallet = new ethers.Wallet("46b63544ad6af04884b846a536926f2efee06d7f154c3b2366bbbaf277266d9f", provider);
  } else {
    // Use first account from local hardhat node
    const accounts = await provider.listAccounts();
    if (accounts.length === 0) {
      throw new Error("No accounts available. Start a local Hardhat node or provide a PRIVATE_KEY");
    }
    wallet = accounts[0];
  }

  console.log("Deploying with account:", wallet.address || await wallet.getAddress());

  // Create contract factory
  const contractFactory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, wallet);

  // Deploy the contract
  console.log("Deploying contract...");
  const pocRegistry = await contractFactory.deploy();
  
  // Wait for deployment
  const deploymentTransaction = pocRegistry.deploymentTransaction();
  if (deploymentTransaction) {
    await deploymentTransaction.wait();
  }
  
  // Get contract address (try different methods for compatibility)
  let address;
  try {
    address = await pocRegistry.getAddress();
  } catch (error) {
    console.log("getAddress() failed, trying alternative methods...");
    address = pocRegistry.target || pocRegistry.address;
  }
  
  if (!address) {
    throw new Error("Could not determine contract address");
  }
  
  console.log("PoCRegistry deployed to:", address);

  // Test the contract by calling a function
  console.log("Testing contract deployment...");

  try {
    const testTx = await pocRegistry.registerPoC(
      ethers.keccak256(ethers.toUtf8Bytes("test-poc-hash")),
      address,
      17,
      "FLASHLOAN",
      "ipfs://test-metadata-uri",
      "HIGH",
      "This is a high risk alert"
    );
    
    await testTx.wait();
    console.log("Test transaction successful:", testTx.hash);
  } catch (error) {
    console.log("Test transaction failed, but contract is deployed:", error.message);
  }

  return address;
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then((address) => {
    console.log("Deployment completed successfully!");
    console.log("Contract address:", address);
    process.exit(0);
  })
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  });