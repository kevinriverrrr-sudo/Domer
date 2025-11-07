#!/bin/bash
# Попытка найти и использовать luac для компиляции

LUAC_PATHS=(
    "/usr/bin/luac"
    "/usr/bin/luac5.1"
    "/usr/bin/luac5.2"
    "/usr/local/bin/luac"
    "luac"
)

for luac in "${LUAC_PATHS[@]}"; do
    if command -v "$luac" &> /dev/null; then
        echo "Found luac: $luac"
        "$luac" -o BP_compiled.luac BP.lua 2>&1
        if [ $? -eq 0 ]; then
            echo "Successfully compiled BP.lua to BP_compiled.luac"
            exit 0
        fi
    fi
done

echo "luac not found, keeping source code"
exit 1
