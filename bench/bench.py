#!/usr/bin/env python3
"""Ollama benchmark — identical on Windows and Bazzite, so the two can be compared.

    python bench/bench.py qwen3:14b            # local Ollama
    python bench/bench.py qwen3:14b --host http://hanz:11434

Fixed prompt, seed and length; one warm-up run (loads the model), then N timed runs.
Appends one JSON line to bench/results.jsonl. Standard library only.
"""
import argparse, json, platform, shutil, statistics, subprocess, time, urllib.request
from pathlib import Path

PROMPT = ("Explain, in about 300 words, how a home network can route requests for "
          "AI inference to whichever machine has a free GPU, and what can go wrong.")


def generate(host, model, num_predict):
    body = json.dumps({
        "model": model, "prompt": PROMPT, "stream": False, "think": False,
        "options": {"seed": 42, "temperature": 0, "num_predict": num_predict, "num_ctx": 4096},
    }).encode()
    req = urllib.request.Request(f"{host}/api/generate", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)


def gpu():
    if not shutil.which("nvidia-smi"):
        return None
    out = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.used,memory.total",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout
    name, drv, used, total = [x.strip() for x in out.splitlines()[0].split(",")]
    return {"name": name, "driver": drv, "vram_used_mib": int(used), "vram_total_mib": int(total)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--host", default="http://127.0.0.1:11434")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--tokens", type=int, default=256)
    a = ap.parse_args()

    print(f"warm-up ({a.model}) ...", flush=True)
    w = generate(a.host, a.model, 16)
    gen, pp = [], []
    for i in range(a.runs):
        r = generate(a.host, a.model, a.tokens)
        gen.append(r["eval_count"] / (r["eval_duration"] / 1e9))
        pp.append(r["prompt_eval_count"] / (r["prompt_eval_duration"] / 1e9))
        print(f"run {i + 1}: {gen[-1]:6.1f} tok/s generate   {pp[-1]:7.1f} tok/s prompt", flush=True)

    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "host": platform.node(),
        "os": f"{platform.system()} {platform.release()}", "model": a.model,
        "load_s": round(w["load_duration"] / 1e9, 2),
        "gen_tok_s": round(statistics.median(gen), 1), "prompt_tok_s": round(statistics.median(pp), 1),
        "gpu": gpu(),
    }
    print(json.dumps(rec, indent=2))
    with open(Path(__file__).with_name("results.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()
