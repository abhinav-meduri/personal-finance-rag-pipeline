#!/bin/bash

# Binary File Checker Script
# Checks for binary files in a directory and optionally deletes them

# Default values
DIRECTORY="."
DELETE_MODE=false
VERBOSE=false
DRY_RUN=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [DIRECTORY]"
    echo ""
    echo "Check for binary files in a directory and optionally delete them"
    echo ""
    echo "Options:"
    echo "  -d, --delete     Delete binary files (default: false)"
    echo "  -v, --verbose    Show verbose output"
    echo "  -n, --dry-run    Show what would be deleted without actually deleting"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Arguments:"
    echo "  DIRECTORY        Directory to check (default: current directory)"
    echo ""
    echo "Examples:"
    echo "  $0 wiki_pages/                    # Check wiki_pages directory"
    echo "  $0 -d wiki_pages/                 # Check and delete binary files"
    echo "  $0 -n -d wiki_pages/              # Dry run - show what would be deleted"
    echo "  $0 -v -d wiki_pages/              # Verbose mode with deletion"
}

# Function to check if file is binary
is_binary_file() {
    local file="$1"
    
    # Use file command to determine file type
    local file_type=$(file -b "$file")
    
    # Check various indicators of binary files
    if [[ "$file_type" =~ ^(gzip|bzip2|ZIP|tar|ELF|Mach-O|PE32|data|image|audio|video) ]] || \
       [[ "$file_type" =~ (compressed|archive|binary|executable) ]] || \
       [[ "$file_type" =~ (JPEG|PNG|GIF|PDF|MP3|MP4|AVI) ]]; then
        return 0  # Is binary
    fi
    
    # Additional check: if file contains null bytes, it's likely binary
    if file "$file" | grep -q "data"; then
        return 0  # Is binary
    fi
    
    # Check for common binary file extensions
    local extension="${file##*.}"
    case "${extension,,}" in
        exe|bin|so|dll|dylib|o|a|lib|jar|zip|gz|tar|bz2|xz|7z|rar|pdf|jpg|jpeg|png|gif|bmp|tiff|mp3|mp4|avi|mov|wmv|flv|webm|ogg|wav|ico|ttf|woff|woff2)
            return 0  # Is binary
            ;;
    esac
    
    return 1  # Not binary
}

# Function to format file size
format_size() {
    local size=$1
    if [ $size -lt 1024 ]; then
        echo "${size}B"
    elif [ $size -lt 1048576 ]; then
        echo "$(($size / 1024))KB"
    else
        echo "$(($size / 1048576))MB"
    fi
}

# Function to process files
process_files() {
    local directory="$1"
    local binary_count=0
    local total_size=0
    local files_deleted=0
    local size_deleted=0
    
    echo -e "${BLUE}Checking directory: $directory${NC}"
    echo ""
    
    # Find all files (not directories)
    while IFS= read -r -d '' file; do
        if [ -f "$file" ]; then
            local file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
            local file_type=$(file -b "$file")
            
            if is_binary_file "$file"; then
                binary_count=$((binary_count + 1))
                total_size=$((total_size + file_size))
                
                if [ "$VERBOSE" = true ]; then
                    echo -e "${RED}BINARY:${NC} $file"
                    echo -e "  Type: $file_type"
                    echo -e "  Size: $(format_size $file_size)"
                    echo ""
                else
                    echo -e "${RED}BINARY:${NC} $file ($(format_size $file_size))"
                fi
                
                # Delete file if requested
                if [ "$DELETE_MODE" = true ]; then
                    if [ "$DRY_RUN" = true ]; then
                        echo -e "${YELLOW}  [DRY RUN] Would delete: $file${NC}"
                    else
                        if rm "$file"; then
                            echo -e "${GREEN}  Deleted: $file${NC}"
                            files_deleted=$((files_deleted + 1))
                            size_deleted=$((size_deleted + file_size))
                        else
                            echo -e "${RED}  Error deleting: $file${NC}"
                        fi
                    fi
                fi
            else
                if [ "$VERBOSE" = true ]; then
                    echo -e "${GREEN}TEXT:${NC} $file ($(format_size $file_size))"
                fi
            fi
        fi
    done < <(find "$directory" -type f -print0)
    
    # Summary
    echo ""
    echo -e "${BLUE}=== SUMMARY ===${NC}"
    echo -e "Binary files found: ${RED}$binary_count${NC}"
    echo -e "Total size of binary files: ${RED}$(format_size $total_size)${NC}"
    
    if [ "$DELETE_MODE" = true ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${YELLOW}Files that would be deleted: $binary_count${NC}"
            echo -e "${YELLOW}Size that would be freed: $(format_size $total_size)${NC}"
        else
            echo -e "${GREEN}Files deleted: $files_deleted${NC}"
            echo -e "${GREEN}Size freed: $(format_size $size_deleted)${NC}"
        fi
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--delete)
            DELETE_MODE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo "Unknown option $1"
            show_usage
            exit 1
            ;;
        *)
            DIRECTORY="$1"
            shift
            ;;
    esac
done

# Check if directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo -e "${RED}Error: Directory '$DIRECTORY' does not exist${NC}"
    exit 1
fi

# Show current settings
echo -e "${BLUE}Binary File Checker${NC}"
echo -e "Directory: $DIRECTORY"
echo -e "Delete mode: $([ "$DELETE_MODE" = true ] && echo -e "${RED}ENABLED${NC}" || echo -e "${GREEN}DISABLED${NC}")"
echo -e "Verbose mode: $([ "$VERBOSE" = true ] && echo -e "${GREEN}ENABLED${NC}" || echo -e "${YELLOW}DISABLED${NC}")"
if [ "$DRY_RUN" = true ]; then
    echo -e "Dry run: ${YELLOW}ENABLED${NC}"
fi
echo ""

# Confirm deletion if not dry run
if [ "$DELETE_MODE" = true ] && [ "$DRY_RUN" = false ]; then
    echo -e "${YELLOW}WARNING: This will permanently delete binary files!${NC}"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    echo ""
fi

# Process files
process_files "$DIRECTORY"
