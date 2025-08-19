#!/usr/bin/env python3
"""
Display Token Minting Script for Raspberry Pi Zero
Shows dishwasher status and token counts, with button minting
"""

import asyncio
import json
import queue
import RPi.GPIO as GPIO
import time
import board
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_st7789 import ST7789
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from spl.token.instructions import mint_to, MintToParams, create_associated_token_account, get_associated_token_address
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from mp3_player import MP3Player

# Display update queue for thread-safe updates
display_update_queue = queue.Queue()

# Initialize MP3 player
mp3_player = MP3Player(port='/dev/serial0')

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins
BUTTON_1_PIN = 17  # Player 1 button
BUTTON_2_PIN = 18  # Player 2 button
MP3_SPEAKER_PIN = 18  # This will trigger the mp3 speaker to play a sound

# Set up the GPIO pins
GPIO.setup(BUTTON_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Hardcoded destination wallets
PLAYER_1_WALLET = "41QHsedtyfNyj6Q2iCDFoGspZ7rqUKu735YNoFLTvw9i"
PLAYER_2_WALLET = "GsfNSuZFrT2r4xzSndnCSs9tTXwt47etPqU8yFVnDcXd"
mint_address = "gyriWKfyFGRLw1a6JuueMZ6ER84WewmicFUa6B3GZJy"
RPC_URL = "https://api.devnet.solana.com"

# Token counts (will be updated)
player1_tokens = 0
player2_tokens = 0

# Initialize display
displayio.release_displays()
spi = board.SPI()
tft_cs = board.D5
tft_dc = board.D24
display_bus = displayio.FourWire(
    spi, command=tft_dc, chip_select=tft_cs,
    reset=board.D25
)
display = ST7789(display_bus, width=280, height=240,
                 rowstart=20, rotation=90)

# Make the display context
splash = displayio.Group()
display.root_group = splash

# Background
color_bitmap = displayio.Bitmap(280, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x303062

bg_sprite = displayio.TileGrid(color_bitmap,
                              pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Title text
title_group = displayio.Group(scale=2, x=10, y=30)
title_text = "Who unloaded"
title_area = label.Label(terminalio.FONT, text=title_text, color=0xFFFFFF)
title_group.append(title_area)
splash.append(title_group)

title_group = displayio.Group(scale=2, x=10, y=60)
title_text = "the dishwasher?"
title_area = label.Label(terminalio.FONT, text=title_text, color=0xFFFFFF)
title_group.append(title_area)
splash.append(title_group)

# Subtitle
subtitle_group = displayio.Group(scale=1, x=60, y=90)
subtitle_text = "Press to mint tokens"
subtitle_area = label.Label(terminalio.FONT, text=subtitle_text, color=0xFFFF00)
subtitle_group.append(subtitle_area)
splash.append(subtitle_group)

# Token counts
token_group = displayio.Group(scale=2, x=20, y=115)

# Player 1 tokens
player1_text = f"Player 1 ({player1_tokens})"
player1_area = label.Label(terminalio.FONT, text=player1_text, color=0xFF0000)
token_group.append(player1_area)

# Player 2 tokens - positioned next to Player 1
player2_text = f"Player 2 ({player2_tokens})"
player2_area = label.Label(terminalio.FONT, text=player2_text, color=0xFF0000)
player2_area.x = 70  # Position next to Player 1 with more space
token_group.append(player2_area)

splash.append(token_group)

# Status text for minting
status_group = displayio.Group(scale=2, x=10, y=140)
status_text = ""
status_area = label.Label(terminalio.FONT, text=status_text, color=0x00FF00)
status_group.append(status_area)
splash.append(status_group)

def show_minting_status(status):
    """Show minting status on display"""
    # Enqueue the status update instead of directly updating
    display_update_queue.put(("status", status))
    print(f"Display: {status}")
 
def clear_minting_status():
    """Clear minting status from display"""
    # Enqueue the status clear instead of directly updating
    display_update_queue.put(("status", ""))

async def get_token_balance(rpc, token_account_address):
    """Get token balance for a specific account"""
    try:
        balance = await rpc.get_token_account_balance(token_account_address)
        if balance.value:
            # Convert from smallest unit to tokens (assuming 9 decimals)
            # Handle both string and int amounts
            amount = balance.value.amount
            if isinstance(amount, str):
                token_amount = int(amount) / 1_000_000_000
            else:
                token_amount = amount / 1_000_000_000
            return token_amount
        else:
            return 0
    except Exception as e:
        print(f"Error getting token balance: {e}")
        return 0

async def update_token_balances():
    """Update token balances from blockchain"""
    global player1_tokens, player2_tokens
    
    keypair = await load_keypair()
    if not keypair:
        return

    async with AsyncClient(RPC_URL) as rpc:
        try:
            # Get Player 1 token account
            player1_owner = Pubkey.from_string(PLAYER_1_WALLET)
            player1_token_account = get_associated_token_address(player1_owner, mint_address)
            
            # Check if Player 1 token account exists
            player1_account_info = await rpc.get_account_info(player1_token_account)
            if player1_account_info.value:
                player1_tokens = await get_token_balance(rpc, player1_token_account)
            else:
                player1_tokens = 0
                print("Player 1 token account not found yet")
            
            # Get Player 2 token account
            player2_owner = Pubkey.from_string(PLAYER_2_WALLET)
            player2_token_account = get_associated_token_address(player2_owner, mint_address)
            
            # Check if Player 2 token account exists
            player2_account_info = await rpc.get_account_info(player2_token_account)
            if player2_account_info.value:
                player2_tokens = await get_token_balance(rpc, player2_token_account)
            else:
                player2_tokens = 0
                print("Player 2 token account not found yet")
            
            # Update display
            update_display()
            print(f"Updated balances - Player 1: {player1_tokens}, Player 2: {player2_tokens}")
            
        except Exception as e:
            print(f"Error updating token balances: {e}")
            # Set default values if there's an error
            player1_tokens = 0
            player2_tokens = 0
            update_display()

def update_display():
    """Update the display with current token counts"""
    # Enqueue the token update instead of directly updating
    display_update_queue.put(("update_tokens", player1_tokens, player2_tokens))

async def load_keypair():
    """Load keypair from JSON file"""
    try:
        with open("waL4uRNa8mErBkbTZVWb4MfXXGfQA7PCfP3hbXS1uEn.json", "r") as f:
            keypair_data = json.load(f)
        return Keypair.from_bytes(keypair_data)
    except FileNotFoundError:
        print("Error: Keypair file not found!")
        return None
    except Exception as e:
        print(f"Error loading keypair: {e}")
        return None

async def check_token_account_exists(rpc, owner, mint_address):
    """Check if associated token account exists"""
    associated_token_account = get_associated_token_address(owner, mint_address)
    
    try:
        account_info = await rpc.get_account_info(associated_token_account)
        return account_info.value is not None, associated_token_account
    except Exception as e:
        print(f"Error checking token account: {e}")
        return False, associated_token_account

async def create_token_account(rpc, payer, owner, mint_address):
    """Create associated token account"""
    associated_token_account = get_associated_token_address(owner, mint_address)
    
    # Get latest blockhash
    recent_blockhash = await rpc.get_latest_blockhash()
    
    # Create associated token account instruction
    create_token_account_instruction = create_associated_token_account(
        payer=payer.pubkey(),
        owner=owner,
        mint=mint_address,
        token_program_id=TOKEN_PROGRAM_ID
    )
    
    # Create message
    message = MessageV0.try_compile(
        payer=payer.pubkey(),
        instructions=[create_token_account_instruction],
        address_lookup_table_accounts=[],
        recent_blockhash=recent_blockhash.value.blockhash
    )
    
    # Create transaction
    transaction = VersionedTransaction(message, [payer])
    
    # Send transaction
    result = await rpc.send_transaction(transaction)
    print(f"✅ Token account created successfully!")
    print(f"Transaction signature: {result.value}")
    
    # Confirm transaction
    confirmation = await rpc.confirm_transaction(result.value)
     
    if confirmation.value:
        print(f"✅ Token account creation confirmed on-chain!")
    else:
        print("⚠️  Token account creation may not have been confirmed")
    
    return associated_token_account

async def mint_token_to_wallet(destination_wallet_address, person_name):
    """Mint token to specified wallet"""
    global player1_tokens, player2_tokens
    
    print(f"Minting token to {person_name}...")
    show_minting_status(f"Minting to {person_name}...")
    
    keypair = await load_keypair()
    if not keypair:
        print("Failed to load keypair")
        show_minting_status("Error: No keypair")
        return
    
    # Use the loaded keypair as both payer and mint authority
    payer = keypair
    mint_authority = keypair
    
    # Destination wallet
    destination_owner = Pubkey.from_string(destination_wallet_address)

    async with AsyncClient(RPC_URL) as rpc:
        print(f"Payer: {payer.pubkey()}")
        print(f"Destination Owner: {destination_owner}")
        print(f"Mint: {mint_address}")
        
        # Check if token account exists for destination wallet
        show_minting_status(f"Checking {person_name} account...")
        exists, associated_token_account = await check_token_account_exists(rpc, destination_owner, mint_address)
        
        if not exists:
            print(f"Token account not found for {person_name}. Creating associated token account...")
            show_minting_status(f"Creating {person_name} account...")
            associated_token_account = await create_token_account(rpc, payer, destination_owner, mint_address)
        else:
            print(f"✅ Token account already exists for {person_name}: {associated_token_account}")
        
        # Amount to mint (in smallest unit) - 1 token
        amount_to_mint = 1000000000
        
        print(f"Destination Token Account: {associated_token_account}")
        print(f"Amount to mint: {amount_to_mint}")
        print(f"Mint authority: {mint_authority.pubkey()}")
         
        # Create mint instruction
        show_minting_status("Creating transaction...")
        mint_instruction = mint_to(
            MintToParams(
                program_id=TOKEN_PROGRAM_ID,
                mint=mint_address,
                dest=associated_token_account,
                mint_authority=mint_authority.pubkey(),
                amount=amount_to_mint
            )
        )
        
        # Get latest blockhash
        show_minting_status("Getting blockhash...")
        recent_blockhash = await rpc.get_latest_blockhash()
        
        # Create message
        message = MessageV0.try_compile(
            payer=payer.pubkey(),
            instructions=[mint_instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash.value.blockhash
        )
        
        # Create transaction
        transaction = VersionedTransaction(message, [payer])
        
        print(f"Mint transaction created successfully")
        
        # Send transaction
        try:
            show_minting_status("Sending transaction...")
            result = await rpc.send_transaction(transaction)
            print(f"✅ Token minted successfully to {person_name}!")
            print(f"Transaction signature: {result.value}")
            
            # Confirm transaction
            show_minting_status("Confirming on-chain...")
            print("Confirming transaction on-chain...")
            confirmation = await rpc.confirm_transaction(result.value, "confirmed")
 
            if confirmation.value:
                print(f"✅ Transaction confirmed on-chain!")
                show_minting_status("Success!!!!!!!!!!!!!!!!")
                # Give the main thread time to process the success message
                await asyncio.sleep(0.5)
                # Update token balances from blockchain
                await update_token_balances()
                # Clear status after a short delay
                await asyncio.sleep(2)
                clear_minting_status()
            else:
                print("⚠️  Transaction may not have been confirmed")
                show_minting_status("⚠️  Not confirmed")
                # Give the main thread time to process the status message
                await asyncio.sleep(2.5)
                clear_minting_status()
                
        except Exception as e:
            print(f"❌ Error minting token to {person_name}: {e}")
            show_minting_status(f"❌ Error: {str(e)[:20]}")
            # Give the main thread time to process the error message
            await asyncio.sleep(3)
            clear_minting_status()

def button_1_callback(channel):
    """Callback function for Player 1 button press"""
    print("Player 1 button pressed! Minting token...")
    # Play MP3 track 3 for Player 1
    if mp3_player.is_connected:
        mp3_player.play_track(3)
    asyncio.run(mint_token_to_wallet(PLAYER_1_WALLET, "Player 1"))

def button_2_callback(channel):
    """Callback function for Player 2 button press"""
    print("Player 2 button pressed! Minting token...")
    # Play MP3 track 2 for Player 2
    if mp3_player.is_connected:
        mp3_player.play_track(2)
    asyncio.run(mint_token_to_wallet(PLAYER_2_WALLET, "Player 2"))

def button_monitor():
    """Monitor button presses"""
    try:
        # Connect to MP3 player
        print("Connecting to MP3 player...")
        if mp3_player.connect():
            print("✅ MP3 player connected successfully!")
            # Set initial volume (adjust as needed)
            mp3_player.set_volume(20)
        else:
            print("⚠️  MP3 player connection failed, continuing without audio")
        
        # Add event detection for both buttons
        GPIO.add_event_detect(BUTTON_1_PIN, GPIO.FALLING, callback=button_1_callback, bouncetime=300)
        GPIO.add_event_detect(BUTTON_2_PIN, GPIO.FALLING, callback=button_2_callback, bouncetime=300)
        
        print(f"Player 1 button connected to GPIO {BUTTON_1_PIN}. Press to mint tokens!")
        print(f"Player 2 button connected to GPIO {BUTTON_2_PIN}. Press to mint tokens!")
        print("Press Ctrl+C to stop.")
        
        # Initial balance update
        print("Loading initial token balances...")
        asyncio.run(update_token_balances())
        
        while True:
            # Process any pending display updates more frequently
            process_display_updates()
            time.sleep(0.05)  # Reduced delay for more responsive updates
            
    except KeyboardInterrupt:
        print("\nStopping button monitor...")
    finally:
        # Clean up GPIO and MP3 player
        GPIO.cleanup()
        if mp3_player.is_connected:
            mp3_player.stop()
            mp3_player.disconnect()
        print("GPIO cleanup completed.")
        print("MP3 player disconnected.")

def process_display_updates():
    """Process display updates from the queue on the main thread"""
    global player1_area, player2_area, status_area
    
    processed_count = 0
    while not display_update_queue.empty():
        try:
            item = display_update_queue.get_nowait()
            if item[0] == "update_tokens":
                _, p1, p2 = item
                player1_area.text = f"Player 1 ({p1:.0f})"
                player2_area.text = f"Player 2 ({p2:.0f})"
                processed_count += 1
                print(f"✅ Updated tokens - Player 1: {p1}, Player 2: {p2}")
            elif item[0] == "status":
                _, status = item
                status_area.text = status
                processed_count += 1
                print(f"✅ Updated status: {status}")
        except queue.Empty:
            break
        except Exception as e:
            print(f"Error processing display update: {e}")
    
    if processed_count > 0:
        print(f"Processed {processed_count} display updates")

if __name__ == "__main__":
    button_monitor() 