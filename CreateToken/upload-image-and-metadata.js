import { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
import { mplCore } from "@metaplex-foundation/mpl-core";
import { promises as fs } from "fs";
import fsSync from "fs";
import {
  createSignerFromKeypair,
  signerIdentity,
  createGenericFile,
} from "@metaplex-foundation/umi";
import { irysUploader } from "@metaplex-foundation/umi-uploader-irys";

// Configuration
const IMAGE_PATH = "./image.png"; // Update this path to your image
const NETWORK = "devnet"; // Change to "mainnet-beta" for mainnet

// Load metadata from JSON file
const TOKEN_METADATA = JSON.parse(
  fsSync.readFileSync("token-metadata.json", "utf8")
);
const TOKEN_NAME = TOKEN_METADATA.name;
const TOKEN_SYMBOL = TOKEN_METADATA.symbol;
const TOKEN_DESCRIPTION = TOKEN_METADATA.description;

async function uploadImageAndMetadata() {
  console.log("🚀 Starting upload process...\n");

  try {
    // Use the RPC endpoint of your choice.
    const umi = createUmi(`https://api.${NETWORK}.solana.com`).use(mplCore());

    // Load default Solana keypair
    let localKeypair;
    try {
      // Try to load from default Solana config location
      const homedir = process.env.HOME || process.env.USERPROFILE;
      const configPath = `${homedir}/.config/solana/id.json`;
      const keypairData = JSON.parse(fsSync.readFileSync(configPath, "utf8"));
      localKeypair = { secretKey: new Uint8Array(keypairData) };
    } catch (error) {
      console.error("❌ Could not load default Solana keypair.");
      console.error("   Make sure you have a Solana keypair configured.");
      console.error("   Run: solana-keygen new");
      return null;
    }

    // Usually Keypairs are saved as Uint8Array, so you
    // need to transform it into a usable keypair.
    let keypair = umi.eddsa.createKeypairFromSecretKey(localKeypair.secretKey);

    // Before Umi can use this Keypair you need to generate
    // a Signer type with it.
    const signer = createSignerFromKeypair(umi, keypair);

    // Tell Umi to use the new signer.
    umi.use(signerIdentity(signer));

    umi.use(irysUploader());

    console.log(`🔑 Loaded wallet: ${signer.publicKey}`);
    console.log(`📡 Connected to ${NETWORK}`);

    // Step 1: Upload the image
    console.log("\n📸 Step 1: Uploading image...", IMAGE_PATH);
    let imageUri;
    try {
      // Read and convert the image file to GenericFile format
      const buffer = await fs.readFile(IMAGE_PATH);
      const file = createGenericFile(buffer, IMAGE_PATH, {
        contentType: "image/png",
      });

      const [uploadedImageUri] = await umi.uploader.upload([file]);
      imageUri = uploadedImageUri;
      console.log(`✅ Image uploaded successfully: ${imageUri}`);
    } catch (error) {
      console.error("❌ Error uploading image:", error.message);
      console.log("💡 Make sure the image file exists at:", IMAGE_PATH);
      console.log(
        "   You can update IMAGE_PATH in the script or create an assets folder with your image."
      );
      return null;
    }

    // Step 2: Upload the metadata JSON
    console.log("\n📄 Step 2: Uploading metadata...");
    const metadataUri = await umi.uploader.uploadJson({
      name: TOKEN_NAME,
      description: TOKEN_DESCRIPTION,
      image: imageUri,
      symbol: TOKEN_SYMBOL,
      attributes: TOKEN_METADATA.attributes,
      properties: {
        files: [
          {
            type: "image/png",
            uri: imageUri,
          },
        ],
        category: "image",
        creators: [
          {
            address: signer.publicKey.toString(),
            share: 100,
          },
        ],
      },
    });

    console.log(`✅ Metadata uploaded successfully: ${metadataUri}`);

    // Summary
    console.log("\n🎉 Upload process completed successfully!");
    console.log("=".repeat(60));
    console.log(`Token Name: ${TOKEN_NAME}`);
    console.log(`Token Symbol: ${TOKEN_SYMBOL}`);
    console.log(`Image URI: ${imageUri}`);
    console.log(`Metadata URI: ${metadataUri}`);
    console.log(`Network: ${NETWORK}`);
    console.log("=".repeat(60));
    console.log("💡 This script uploads image and metadata only.");
    console.log(
      "   To mint a token, use the mint-token-with-metadata.js script."
    );

    return metadataUri; // Return the metadata URI for use in mint script
  } catch (error) {
    console.error("❌ Error during upload process:", error);

    // Provide helpful error messages
    if (error.message.includes("insufficient funds")) {
      console.log(
        "\n💡 Tip: You need more SOL in your wallet. Get devnet SOL from:"
      );
      console.log("   https://faucet.solana.com/");
    } else if (error.message.includes("ENOENT")) {
      console.log(
        "\n💡 Tip: Image file not found. Make sure the image exists at the specified path."
      );
      console.log(`   Expected path: ${IMAGE_PATH}`);
    }
    return null;
  }
}

// Run the script and export the function
if (import.meta.url === `file://${process.argv[1]}`) {
  uploadImageAndMetadata().catch(console.error);
}

export { uploadImageAndMetadata };
