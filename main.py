import os
import json
from datetime import datetime
import time
import argparse
from dotenv import load_dotenv
from litellm import completion, completion_cost

load_dotenv()

def get_response(user_prompt: str, system_prompt: str|None=None, model="openai/gpt-4o-mini") -> tuple[str, float, float]:
    messages = [
        {"role": "user", "content": user_prompt},
    ]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    start_time = time.time()
    response = completion(
        model=model,
        messages=messages,
    )
    end_time = time.time()
    total_time = end_time - start_time
    cost = completion_cost(response)
    return response.choices[0].message.content, cost, total_time


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    user_group = parser.add_mutually_exclusive_group(required=True)
    user_group.add_argument("--user-prompt", type=str, help="Provide user prompt directly")
    user_group.add_argument("--user-prompt-file", type=str, help="Read user prompt from file")

    system_group = parser.add_mutually_exclusive_group(required=False)
    system_group.add_argument("--system-prompt", type=str, help="Provide system prompt directly")
    system_group.add_argument("--system-prompt-file", type=str, help="Read system prompt from file")

    parser.add_argument("--models", type=str, default="openai/gpt-4o-mini", help="Comma separated list of models to use")
    args = parser.parse_args()

    user_prompt = args.user_prompt
    prompt_key = ""
    
    if args.user_prompt_file:
        args.user_prompt_file = os.path.expanduser(args.user_prompt_file)
        with open(args.user_prompt_file, "r") as f:
            user_prompt = f.read()
        prompt_key = os.path.basename(args.user_prompt_file)
    elif args.user_prompt:
        prompt_key = args.user_prompt[:30] + ("..." if len(args.user_prompt) > 30 else "")

    system_prompt = args.system_prompt
    if args.system_prompt_file:
        args.system_prompt_file = os.path.expanduser(args.system_prompt_file)
        with open(args.system_prompt_file, "r") as f:
            system_prompt = f.read()

    models = args.models.split(",")
    results = []
    for model in models:
        try:
            response, cost, total_time = get_response(user_prompt, system_prompt, model)
            results.append({
                "model": model,
                "response": response,
                "cost": cost,
                "total_time": total_time,
                "prompt": prompt_key,
            })
        except Exception as e:
            print(f"Error with model {model}: {e}")
            results.append({
                "model": model,
                "response": str(e),
                "cost": 0,
                "total_time": 0,
                "prompt": prompt_key,
            })
            continue
        print(f"Model: {model}")
        print(f"Response:\n{response}")
        print(f"Cost: {cost:.4f} USD")
        print(f"Total time: {total_time:.4f} seconds")
        print(f"\n\n{'-'*100}\n\n")

    os.makedirs("outputs", exist_ok=True)
    today_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output_file = f"outputs/results-{today_timestamp}.json"
    
    # Add metadata to the results
    output_data = {
        "timestamp": today_timestamp,
        "user_prompt": user_prompt,
        "system_prompt": system_prompt,
        "prompt": prompt_key,
        "results": results
    }
    
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)
    print(f"Results saved to {output_file}")
