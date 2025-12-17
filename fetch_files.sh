#!/bin/bash

BASE_URL="https://raw.githubusercontent.com/maneatingape/advent-of-code-rust/main/src"

# Fetch utilities
mkdir -p src/util
UTILS="ansi bitset grid hash heap integer iter math md5 parse point slice thread"
for util in $UTILS; do
    echo "Fetching util/$util.rs..."
    curl -s "$BASE_URL/util/$util.rs" -o "src/util/$util.rs"
done

# Fetch days
# Repo uses day01.rs, day02.rs...
# Local uses day1.rs, day2.rs...
for i in {1..12}; do
    # Format with leading zero for repo
    if [ $i -lt 10 ]; then
        REPO_DAY="day0$i"
    else
        REPO_DAY="day$i"
    fi
    
    # Local filename
    LOCAL_DAY="day$i"
    
    echo "Fetching year2025/$REPO_DAY.rs to src/$LOCAL_DAY.rs..."
    curl -s "$BASE_URL/year2025/$REPO_DAY.rs" -o "src/$LOCAL_DAY.rs"
done
