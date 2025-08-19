import {
  Keypair,
  Connection,
  clusterApiUrl,
  sendAndConfirmTransaction,
  PublicKey,
  Transaction,
} from "@solana/web3.js";
import {
  createMint,
  getOrCreateAssociatedTokenAccount,
  mintTo,
} from "@solana/spl-token";
import { createCreateMetadataAccountV3Instruction } from "@metaplex-foundation/mpl-token-metadata";
import { uploadImageAndMetadata } from "./upload-image-and-metadata.js";
import fs from "fs";

// Configuration
const NETWORK = "devnet"; // Change to "mainnet-beta" for mainnet

// Load metadata from JSON file
const TOKEN_METADATA = JSON.parse(
  fs.readFileSync("token-metadata.json", "utf8")
);
const TOKEN_NAME = TOKEN_METADATA.name;
const TOKEN_SYMBOL = TOKEN_METADATA.symbol;
const TOKEN_DECIMALS = TOKEN_METADATA.decimals || 9; // Default to 9 if not specified
const MINT_AMOUNT = TOKEN_METADATA.mintAmount || 1000; // Default to 1000 if not specified

function loadKeypairFromFile(filename) {
  try {
    const keypairData = JSON.parse(fs.readFileSync(filename, "utf8"));
    return Keypair.fromSecretKey(new Uint8Array(keypairData));
  } catch (error) {
    console.error(`❌ Error loading keypair from ${filename}:`, error.message);
    return null;
  }
}

function loadOrCreateMintKeypair() {
  const MINT_ADDRESS_FILE = "token-mint-address.json";

  try {
    // Check if token mint address file exists
    if (fs.existsSync(MINT_ADDRESS_FILE)) {
      console.log(
        "📁 Found existing token mint address file, using saved keypair..."
      );
      return loadKeypairFromFile(MINT_ADDRESS_FILE);
    } else {
      // Create new keypair for minting
      console.log(
        "🆕 No existing token mint address found, creating new keypair..."
      );
      const newKeypair = Keypair.generate();

      // Save the new keypair to file (as a proper keypair file)
      const keypairData = Array.from(newKeypair.secretKey);
      fs.writeFileSync(MINT_ADDRESS_FILE, JSON.stringify(keypairData, null, 2));

      console.log(
        `✅ Created new mint keypair: ${newKeypair.publicKey.toString()}`
      );
      console.log(`💾 Saved to: ${MINT_ADDRESS_FILE}`);

      return newKeypair;
    }
  } catch (error) {
    console.error("❌ Error in loadOrCreateMintKeypair:", error.message);
    return null;
  }
}

const MINT_KEYPAIR = loadOrCreateMintKeypair();

async function mintTokenWithMetadata() {
  console.log("🚀 Starting token minting process...\n");

  try {
    // First, upload image and metadata to get the metadata URI
    console.log("📤 Step 1: Uploading image and metadata...");
    const metadataUri = await uploadImageAndMetadata();

    if (!metadataUri) {
      console.error(
        "❌ Failed to upload image and metadata. Cannot proceed with minting."
      );
      return;
    }

    console.log(`✅ Got metadata URI: ${metadataUri}`);

    // Load wallet keypair for paying transactions
    const walletKeypair = loadKeypairFromFile("wallet.json");
    if (!walletKeypair) {
      console.error("❌ Could not load wallet.json. Cannot proceed.");
      return;
    }

    // Now proceed with token creation
    console.log("\n🪙 Step 2: Creating and minting token...");

    if (!MINT_KEYPAIR) {
      console.error("❌ Could not load mint keypair. Cannot proceed.");
      return;
    }

    // Connect to Solana
    const connection = new Connection(clusterApiUrl(NETWORK), "confirmed");

    // Check wallet balance
    const balance = await connection.getBalance(walletKeypair.publicKey);
    console.log(`💰 Wallet balance: ${balance / 1e9} SOL`);

    if (balance < 0.1 * 1e9) {
      console.log(
        "⚠️  Low balance! You might need more SOL for this operation."
      );
      console.log(
        `If you are on devnet you can get devnet SOL from: https://faucet.solana.com/`
      );
    }

    // Create the mint
    console.log("Creating token mint...");
    const mint = await createMint(
      connection,
      walletKeypair, // Use wallet keypair as payer
      walletKeypair.publicKey, // Mint authority
      walletKeypair.publicKey, // Freeze authority
      TOKEN_DECIMALS,
      MINT_KEYPAIR
    );

    console.log(`✅ Token mint created: ${mint.toString()}`);

    // Create associated token account for the wallet
    console.log("Creating associated token account...");
    const associatedTokenAccount = await getOrCreateAssociatedTokenAccount(
      connection,
      walletKeypair, // Use wallet keypair as payer
      mint,
      walletKeypair.publicKey // Owner is the wallet
    );

    console.log(
      `✅ Associated token account: ${associatedTokenAccount.address.toString()}`
    );

    // Mint tokens to the wallet
    console.log(`Minting ${MINT_AMOUNT} tokens...`);
    const mintTx = await mintTo(
      connection,
      walletKeypair, // Use wallet keypair as payer
      mint,
      associatedTokenAccount.address,
      walletKeypair, // Mint authority
      MINT_AMOUNT * Math.pow(10, TOKEN_DECIMALS)
    );

    console.log(`✅ Tokens minted successfully! Transaction: ${mintTx}`);

    // Create metadata account
    console.log("Creating metadata account...");
    const metadataAccount = PublicKey.findProgramAddressSync(
      [
        Buffer.from("metadata"),
        new PublicKey("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s").toBuffer(),
        mint.toBuffer(),
      ],
      new PublicKey("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
    )[0];

    const createMetadataInstruction = createCreateMetadataAccountV3Instruction(
      {
        metadata: metadataAccount,
        mint: mint,
        mintAuthority: walletKeypair.publicKey,
        payer: walletKeypair.publicKey, // Use wallet keypair as payer
        updateAuthority: walletKeypair.publicKey,
      },
      {
        createMetadataAccountArgsV3: {
          data: {
            name: TOKEN_NAME,
            symbol: TOKEN_SYMBOL,
            uri: metadataUri,
            sellerFeeBasisPoints: 0,
            creators: [
              {
                address: walletKeypair.publicKey, // Use wallet keypair as creator
                verified: true,
                share: 100,
              },
            ],
            collection: null,
            uses: null,
          },
          isMutable: true,
          collectionDetails: null,
        },
      }
    );

    const transaction = new Transaction().add(createMetadataInstruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      walletKeypair,
    ]);

    console.log(`✅ Metadata account created! Transaction: ${signature}`);

    // Summary
    console.log("\n🎉 Token creation completed successfully!");
    console.log("=".repeat(60));
    console.log(`Token Name: ${TOKEN_NAME}`);
    console.log(`Token Symbol: ${TOKEN_SYMBOL}`);
    console.log(`Token Mint: ${mint.toString()}`);
    console.log(`Metadata URI: ${metadataUri}`);
    console.log(`Network: ${NETWORK}`);
    console.log(`Initial Supply: ${MINT_AMOUNT} tokens`);
    console.log("=".repeat(60));
    console.log("💡 Your token is now ready to use on the Raspberry Pi!");
    console.log(
      `   Update your Pi script with mint address: ${mint.toString()}`
    );
  } catch (error) {
    console.error("❌ Error during token creation:", error);
    if (error.message.includes("insufficient funds")) {
      console.log(
        "\n💡 Tip: You need more SOL in your wallet. Get devnet SOL from:"
      );
      console.log("   https://faucet.solana.com/");
    }
  }
}

// Run the script
mintTokenWithMetadata().catch(console.error);
