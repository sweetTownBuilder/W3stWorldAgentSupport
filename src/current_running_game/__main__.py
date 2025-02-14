import json
from typing import Dict, Any

import requests
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey


def main(program_address_str: str, rpc_url: str, ipfs_url: str) -> Dict[str, Any]:
    client = Client(rpc_url)
    program_address = Pubkey.from_string(program_address_str)
    game_manager_addr, _ = Pubkey.find_program_address([b"game_manager"], program_address)
    res = client.get_account_info(game_manager_addr, commitment=Confirmed).value
    decoded_data = res.data
    # # 分段提取字节
    next_game_bytes = decoded_data[72:80]

    current_game = (int.from_bytes(next_game_bytes, byteorder='little') - 1).to_bytes(8, byteorder='little')

    current_game_pda, _ = Pubkey.find_program_address([b"game_info", current_game], program_address)
    game_res = client.get_account_info(current_game_pda, commitment=Confirmed).value
    content = game_res.data[8:]
    # 逐个字段解析
    offset = 0

    # 1. game_id (u64)
    game_id = int.from_bytes(content[offset:offset + 8], "little")
    offset += 8

    # 2. meta_data (String)
    meta_data_length = int.from_bytes(content[offset:offset + 4], "little")
    offset += 4
    meta_data = content[offset:offset + meta_data_length].decode("utf-8")
    offset += meta_data_length

    # 3-5. 时间字段 (i64)
    start_time = int.from_bytes(content[offset:offset + 8], "little", signed=True)
    offset += 8
    end_time = int.from_bytes(content[offset:offset + 8], "little", signed=True)
    offset += 8
    event_end_time = int.from_bytes(content[offset:offset + 8], "little", signed=True)
    offset += 8

    # 6-8. 数值字段 (u64)
    total = int.from_bytes(content[offset:offset + 8], "little")
    offset += 8
    guess_win = int.from_bytes(content[offset:offset + 8], "little")
    offset += 8
    guess_lose = int.from_bytes(content[offset:offset + 8], "little")
    offset += 8

    # 9-10. 结果字段 (u8)
    first_result = content[offset]
    offset += 1
    final_result = content[offset]
    offset += 1

    # 11. final_time (i64)
    final_time = int.from_bytes(content[offset:offset + 8], "little", signed=True)
    offset += 8

    # 12. challenge_proof (String)
    challenge_proof_length = int.from_bytes(content[offset:offset + 4], "little")
    offset += 4
    challenge_proof = content[offset:offset + challenge_proof_length].decode("utf-8")
    offset += challenge_proof_length

    # 13-16. 剩余字段
    game_user = int.from_bytes(content[offset:offset + 8], "little")
    offset += 8
    game_close = content[offset]
    offset += 1
    game_close_time = int.from_bytes(content[offset:offset + 8], "little", signed=True)
    # offset += 8
    # bump = content[offset]

    response = requests.request("GET", ipfs_url + "/ipfs/" + meta_data)
    meta_data_json = response.json()

    return {
        "result": json.dumps({
            "game_name": meta_data_json['title'],
            "game_win_coin": meta_data_json['guess']['guess_win']['coin_name'],
            "game_loss_coin": meta_data_json['guess']['guess_loss']['coin_name'],
            "game_id": game_id,
            "start_time": start_time,
            "end_time": end_time,
            "event_end_time": event_end_time,
            "total": float(total) / 1000000000.0,
            "guess_win": float(guess_win) / 1000000000.0,
            "guess_lose": float(guess_lose) / 1000000000.0,
            "first_result": first_result,
            "final_result": final_result,
            "final_time": final_time,
            "challenge_proof": challenge_proof,
            "game_user": game_user,
            "game_close": game_close == 1,
            "game_close_time": game_close_time,
        }, ensure_ascii=False),
    }

# 示例调用
if __name__ == "__main__":
    result = main(
        program_address_str="GutccLpNg3B9Wb28AcVmSBvXDimdHBz8qEjpHMW1o56u",
        rpc_url="https://solana-devnet.g.alchemy.com/v2/H0Ot6fdDt0o_GO6e1hK14xswzrss64R9",
        ipfs_url="https://identityomni.mypinata.cloud",
    )

    print(result)
