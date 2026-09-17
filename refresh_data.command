#!/bin/bash

cd "/Users/benetchebarne/Documents/Data_Project_end_to_end"

echo "Starting job market data refresh..."
echo ""

python3 dataingestion.py

echo ""
echo "================================"
echo "Job market refresh complete."
echo "================================"
echo ""
read -p "Press Enter to close..."
