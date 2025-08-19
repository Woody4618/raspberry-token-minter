# Create a Solana SPL token with image and metadata


An easy way to create a Solana SPL token with image and metadata using js. 

Prerequisites:
- [Solana CLI tools](https://solana.com/docs/intro/installation)
- As wallet it will either use the default [solana wallet](https://solana.com/docs/intro/installation#create-wallet) or the `src/wallet.json` file where paste your wallet of choice.

## 🖼️ Step 1: Prepare Token Metadata

### Update the JSON metadata file

Edit `src/token-metadata.json` with your token details:

```json
{
  "name": "Dishewasher Token",
  "symbol": "DISH",
  "description": "Reward tokens for completing household chores like unloading the dishwasher. Each token represents a completed task and can be collected, traded, or used as proof of contribution to household duties.",
  "decimals": 6,
  "mintAmount": 1000,
  "network": "devnet",
  "image": "Will be replaced automatically",
  "attributes": [
    {
      "trait_type": "Category",
      "value": "Household Chores"
    },
    {
      "trait_type": "Task Type",
      "value": "Dishwasher Unloading"
    }
  ]
}
```

- Change the network to `mainnet-beta` if you want to deploy to mainnet. (required mainnet sol in your wallet)
- Change the mintAmount to the amount of tokens you want to mint.
- Change the decimals to the number of decimals you want your token to have.
- Change the attributes to your own.

## 🖼️ Step 2: Add your image

Replace the `src/image.png` with your own. Recommendation: 512x512px for example. 

## 🔑 Step 3: Create a vanity address for your token (optional)

This step is optional if you don't want a cool vanity address for your token.
The command creates a token address that starts with a prefix of your choice. Everything above 4 letters will take a long time to generate. Replace `TEST:1` with your prefix you want your token to have.
First you need to install the [solana-cli](https://solana.com/docs/intro/installation) tool then run the command.
_Note: This will overwrite the token-mint-address.json file. If you want to keep it, rename it to something else._

```bash
cd src
solana-keygen grind --starts-with TEST:1 | tee /dev/tty | grep -oE '[1-9A-HJ-NP-Za-km-z]{32,44}\.json' | head -n1 | xargs -I{} mv {} token-mint-address.json
```

This will generate a keypair file that we will be used as the address for you token.

## 📤 Step 4: Create the token

Install the dependencies

```bash
yarn install
```

Mint the token with the following command:

```bash
node src/mint-token-with-metadata.js
```

This creates your token on Solana and returns the mint address. 
It also mints you 1000 tokens to your wallet.

You can now for example transfer this token to your wallet.

```bash
spl-token transfer <mint> 1000 <yourWallet> --fund-recipient
```

Add `-um` for mainnet `-ud` for devnet depending on your network.

From here you can now easily interact with your token using the Solana [Spl token CLI](https://solana.com/docs/tokens).


Notes:

If you only need the metadata url, you can run the following command:

```bash
node src/upload-image-and-metadata.js
```
