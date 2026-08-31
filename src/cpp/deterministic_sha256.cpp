// =============================================================================
// deterministic_sha256.cpp
// =============================================================================
// Deterministic SHA‑256 file hashing for ERA5 pipeline artifact validation.
//
// This module provides a minimal, reproducible, boundary‑safe hashing function
// used across Branch 2 (Stages 1–4) to verify artifact integrity.
//
// Design goals:
//   • deterministic output across platforms
//   • minimal dependencies (OpenSSL only)
//   • safe streaming of large files
//   • no buffering surprises
//   • no hidden state
//
// Used for:
//   • GRIB file digests (Stage 1)
//   • hourly/variable‑split parquet digests (Stage 2)
//   • merged chunk digests (Stage 3)
//   • tensor digests (Stage 4)
//
// =============================================================================

#include <openssl/sha.h>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <vector>
#include <stdexcept>

// =============================================================================
// sha256_file(path)
// =============================================================================
// Computes the SHA‑256 digest of a file at `path` using a deterministic,
// streaming approach. Returns a lowercase hexadecimal string.
//
// Throws:
//   std::runtime_error if the file cannot be opened.
//
// Notes:
//   • Uses an 8 KB buffer for stable performance.
//   • No memory‑mapping (avoids platform‑dependent behavior).
//   • No concurrency; caller handles parallelism.
// =============================================================================
std::string sha256_file(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + path);
    }

    SHA256_CTX ctx;
    SHA256_Init(&ctx);

    std::vector<unsigned char> buffer(8192);

    while (file.good()) {
        file.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
        SHA256_Update(&ctx, buffer.data(), file.gcount());
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_Final(hash, &ctx);

    std::ostringstream out;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        out << std::hex << std::setw(2) << std::setfill('0')
            << static_cast<int>(hash[i]);
    }

    return out.str();
}
