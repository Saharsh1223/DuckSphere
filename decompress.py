import zstandard as zstd

your_filename = "lichess_db_puzzle.csv.zst"
with open(your_filename, "rb") as f:
    data = f.read()

dctx = zstd.ZstdDecompressor()
decompressed = dctx.decompress(data)
