# Raspberry Pi Token Minter

A fun project that rewards household members with Solana tokens when they unload the dishwasher! (Can of course be for anything else as well) Built for Raspberry Pi with display, buttons, and MP3 audio feedback.

![IMG_9235](https://github.com/user-attachments/assets/dacd24cc-775c-4dd7-95cf-5c43074b887a)


## 🎯 Overview

This project creates a custom Solana token and deploys it to a Raspberry Pi with:

- Physical buttons for each person
- ST7789 display showing token counts
- MP3 audio feedback for button presses
- Automatic token minting to Solana wallets

## 🚀 Getting Started

### Prerequisites

- Solana CLI tools installed (https://docs.solana.com/cli/install-solana-cli)
- Raspberry Pi (Zero2 WH recommended)
- ST7789V2 display (https://www.amazon.de/dp/B0CDPYYQ74?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)
- MP3-TF-16P audio module (https://www.amazon.de/dp/B0DRGCC1M6?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_2)
- 2 push buttons (https://www.amazon.de/dp/B07WPBQXJ9?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1 )
- Micro SD card with MP3 files
- As a power solution you can either plug it into a power plug or use a PiSugar2 or a Geekworm X306 V1.3 Ultra-Thin UPS Shield for Raspberry Pi Zero 2. Both work great with the RaspberryPi Zero 2WH 

# Creating the token

Prerequisites:

- [Solana CLI tools](https://solana.com/docs/intro/installation)
- As wallet it will either use the default [solana wallet](https://solana.com/docs/intro/installation#create-wallet) or the `CreateToken/wallet.json` file where you paste your wallet of choice.

## 🖼️ Step 1: Prepare Token Metadata

### Update the JSON metadata file

Edit `CreateToken/token-metadata.json` with your token details:

```json
{
  "name": "Dishwasher Token",
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

- Change the network to `mainnet-beta` if you want to deploy to mainnet. (requires mainnet SOL in your wallet)
- Change the mintAmount to the amount of tokens you want to mint.
- Change the decimals to the number of decimals you want your token to have.
- Change the attributes to your own.

## 🖼️ Step 2: Add your image

Replace the `CreateToken/image.png` with your own. Recommendation: 512x512px for example.

## 🔑 Step 3: Create a vanity address for your token (optional)

This step is optional if you don't want a cool vanity address for your token.
The command creates a token address that starts with a prefix of your choice. Everything above 4 letters will take a long time to generate. Replace `TEST:1` with your prefix you want your token to have.
First you need to install the [solana-cli](https://solana.com/docs/intro/installation) tool then run the command.
_Note: This will overwrite the CreateToken/token-mint-address.json file. If you want to keep it, rename it to something else._

```bash
cd CreateToken
solana-keygen grind --starts-with TEST:1 | tee /dev/tty | grep -oE '[1-9A-HJ-NP-Za-km-z]{32,44}\.json' | head -n1 | xargs -I{} mv {} token-mint-address.json
```

This will generate a keypair file that will be used as the address for your token.

## 📤 Step 4: Create the token

Install the dependencies (Node.js):

```bash
yarn install
```

Mint the token with the following command:

```bash
cd CreateToken
node mint-token-with-metadata.js
```

This creates your token on Solana and returns the mint address.
It also mints you 1000 tokens to your wallet.

You can now for example transfer this token to your wallet.

```bash
spl-token transfer <mint> 1000 <yourWallet> --fund-recipient
```

Add `-um` for mainnet `-ud` for devnet depending on your network.

From here you can now easily interact with your token using the Solana [Spl token CLI](https://solana.com/docs/tokens).

## ⚙️ Step 5: Configure the Script

### Update wallet addresses

Edit `raspberry/button_token_mint_with_disply_and_mp3.py` and replace:

- `PLAYER_1_WALLET` with the Player 1 wallet address
- `PLAYER_2_WALLET` with the Player 2 wallet address

### Update token mint address

Replace the hardcoded `mint_address` with your token's mint address from step 4.

## 🍓 Step 6: Deploy to Raspberry Pi

### Copy files to Raspberry Pi

```bash
# Copy the whole raspberry folder to your pi
scp -r raspberry pi@YOUR_PI_NETWORK_NAME:/home/pi/
```

### SSH into your Pi

```bash
ssh pi@YOUR_PI_IP
```

### Install Python dependencies

```bash
cd ~/raspberry
pip3 install -r raspberry/requirements.txt
```

Note: You may need to add `--break-system-packages` to the pip3 install command depending on your raspberry pi operating system.

### Prepare MP3 files

Create folder structure on your mircoSD card:

```
SD Card Root/
├── 01/          # Folder 1
│   ├── 001.mp3  # Test sound
│   ├── 002.mp3  # Player 2 sound
│   └── 003.mp3  # Player 1 sound
```

## 🎮 Step 7: Run on Raspberry Pi

### Connect hardware

<img width="1348" alt="image" src="https://github.com/user-attachments/assets/cab48154-ee3d-4ed2-b9d5-a046f316b50f" />


- Connect ST7789 display to GPIO pins (D5, D24, D25) See [README_ST7789.md](README_ST7789.md) for more information.
- Connect buttons to GPIO 17 and 18
- Connect MP3 module to serial port See [README_MP3.md](README_MP3.md) for more information.
- Insert SD card with MP3 files

When everything is connected it should look somewhat like this: 

![IMG_9236](https://github.com/user-attachments/assets/cb2ef603-76bb-4a30-9198-4ed44e05a26d)


### Run the script

```bash
python3 raspberry/button_token_mint_with_disply_and_mp3.py
```

## 🎯 How It Works

1. **Button Press**: When a player presses their button, it plays their unique MP3 sound
2. **Token Minting**: Automatically mints 1 token to their Solana wallet
3. **Display Update**: Shows current token counts for both players
4. **Blockchain Confirmation**: Waits for transaction confirmation before updating display

## 🔧 Troubleshooting

### MP3 not playing?

- Check SD card format (FAT32)
- Verify file naming (001.mp3, 002.mp3, 003.mp3)
- Check serial connection to MP3 module


### Display not working?

- Verify GPIO connections
- Check SPI configuration
- Ensure display library is installed

### Token minting fails?

- Check Solana devnet connection
- Verify wallet addresses
- Ensure keypair file is accessible on the Pi

## 📁 File Structure

```
raspberry-token-minter/
├── CreateToken/                 # Token creation scripts (Node)
│   ├── mint-token-with-metadata.js
│   ├── upload-image-and-metadata.js
│   ├── token-metadata.json
│   ├── image.png
│   └── wallet.json (optional)
├── raspberry/                   # Raspberry Pi runtime (Python)
│   ├── button_token_mint_with_disply_and_mp3.py
│   └── requirements.txt
│   └── wallet.json (The keypair used to create the token. Needs to be the mint authority)
│   └── mp3_player.py                # MP3 player library
├── README_ST7789.md             # ST7789 display guide
├── README_MP3.md                # MP3 module guide
└── README.md                    # This guide
```

## 🎵 Audio Files

The MP3 files should be:

- **001.mp3**: Startup/test sound
- **002.mp3**: Player 2 reward sound
- **003.mp3**: Player 1 reward sound

## 🔌 GPIO Pinout

- **Display**: D5 (CS), D24 (DC), D25 (Reset)
- **Player 1 Button**: GPIO 17
- **Player 2 Button**: GPIO 18
- **MP3 Module**: Serial port (/dev/serial0)

## 🚀 Future Enhancements

- Add more household members
- Implement different token amounts for different chores
- Add web dashboard for token tracking
- Integrate with other smart home devices

## 📚 Resources

- [Solana Documentation](https://docs.solana.com/)
- [Raspberry Pi GPIO](https://www.raspberrypi.org/documentation/usage/gpio/)
- [MP3-TF-16P Module](https://www.dfrobot.com/product-1121.html)

---

**Happy Dishwashing! 🧽✨**
