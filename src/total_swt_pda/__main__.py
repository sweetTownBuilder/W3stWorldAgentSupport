import hashlib
import json
from typing import Dict, Any

import base58
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.rpc.types import MemcmpOpts
from solders.pubkey import Pubkey


def main(program_address_str: str, rpc_url: str) -> Dict[str, Any]:
    client = Client(rpc_url)
    program_address = Pubkey.from_string(program_address_str)
    name = "account:UserSwt"
    discriminator = hashlib.sha256(name.encode("utf-8")).digest()[:8]  # 取前8字节
    all_pda_address = client.get_program_accounts(program_address, filters=[MemcmpOpts(
        offset=0,
        bytes=base58.b58encode(discriminator).decode("utf-8"),
    )], commitment=Confirmed).value
    all_amount_gt_500_account = []
    for account_info in all_pda_address:
        amount = int.from_bytes(account_info.account.data[8:16], "little", signed=True)
        if amount > 500:
            all_amount_gt_500_account.append({
                "account_address": account_info.pubkey.__str__(),
                "amount": amount,
            })
    return {
        "result": json.dumps(all_amount_gt_500_account),
    }


# 示例调用
if __name__ == "__main__":
    result = main(
        program_address_str="7UgwXR4Z1c8euj8J2AJUTUEiA8NdRkcdKFqANv49bQVg",
        rpc_url="https://solana-devnet.g.alchemy.com/v2/H0Ot6fdDt0o_GO6e1hK14xswzrss64R9",
    )

    print(result)
