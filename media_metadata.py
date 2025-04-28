import os
import sys
import argparse
import sqlite3
import datetime
import subprocess

try:
    import exifread  # Images se EXIF data extract karne ke liye
except ImportError:
    print("Please install exifread: pip install exifread")
    sys.exit(1)

try:
    from mutagen import File as MutagenFile  # Audio metadata extract karne ke liye
except ImportError:
    print("Please install mutagen: pip install mutagen")
    sys.exit(1)

# Supported file extensions ki list
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.tiff', '.png',  # images
                        '.mp4', '.mov', '.avi', '.mkv',       # videos
                        '.mp3', '.flac', '.wav', '.aac']       # audio

def create_table(conn):
    """Agar pehle se table na ho toh SQLite database mein media_metadata table create karta hai."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS media_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE,
        file_format TEXT,
        resolution TEXT,
        duration REAL,
        geolocation TEXT,
        file_size INTEGER,
        date_created TEXT,
        date_modified TEXT
    );
    """
    try:
        conn.execute(create_table_sql)
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}", file=sys.stderr)

def convert_to_degrees(value):
    """
    EXIF GPS coordinates ko decimal degrees mein convert karta hai.
    Input 'value' se ummeed ki jaati hai ki usme teen components (degrees, minutes, seconds) hon.
    """
    try:
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)
    except Exception as e:
        print(f"Error converting GPS coordinates: {e}", file=sys.stderr)
        return None

def extract_image_metadata(file_path, metadata):
    """Exifread ka use karke image files se metadata extract karta hai."""
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            # Agar available ho toh resolution extract karo
            if 'EXIF ExifImageWidth' in tags and 'EXIF ExifImageLength' in tags:
                width = str(tags['EXIF ExifImageWidth'])
                height = str(tags['EXIF ExifImageLength'])
                metadata['resolution'] = f"{width}x{height}"
            # Agar available ho toh geolocation extract karo
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat = convert_to_degrees(tags['GPS GPSLatitude'])
                lon = convert_to_degrees(tags['GPS GPSLongitude'])
                if lat is not None and lon is not None:
                    metadata['geolocation'] = f"{lat},{lon}"
    except Exception as e:
        print(f"Error extracting image metadata for {file_path}: {e}", file=sys.stderr)
    return metadata

def extract_video_metadata(file_path, metadata):
    """Ffprobe ka use karke video files se metadata extract karta hai."""
    try:
        # ffprobe command jo video ke width, height, aur duration extract karta hai
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=width,height,duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        output = result.stdout.splitlines()
        if len(output) >= 3:
            width = output[0].strip()
            height = output[1].strip()
            duration = output[2].strip()
            metadata['resolution'] = f"{width}x{height}"
            metadata['duration'] = float(duration) if duration else None
    except Exception as e:
        print(f"Error extracting video metadata for {file_path}: {e}", file=sys.stderr)
    return metadata

def extract_audio_metadata(file_path, metadata):
    """Mutagen ka upyog karke audio files se metadata extract karta hai."""
    try:
        audio = MutagenFile(file_path)
        if audio and audio.info:
            duration = audio.info.length
            metadata['duration'] = duration
            # Audio files mein aam taur par resolution ya geolocation metadata nahi hota
    except Exception as e:
        print(f"Error extracting audio metadata for {file_path}: {e}", file=sys.stderr)
    return metadata

def extract_metadata(file_path):
    """
    Diye gaye file se metadata extract karta hai.
    Ek dictionary return karta hai jisme file path, format, resolution, duration, geolocation, file size, aur timestamps shamil hain.
    """
    metadata = {
        'file_path': file_path,
        'file_format': os.path.splitext(file_path)[1].lower(),
        'resolution': None,
        'duration': None,
        'geolocation': None,
        'file_size': None,
        'date_created': None,
        'date_modified': None
    }
    # File size aur timestamps retrieve karo
    try:
        stat = os.stat(file_path)
        metadata['file_size'] = stat.st_size
        metadata['date_created'] = datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        metadata['date_modified'] = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error accessing file stats for {file_path}: {e}", file=sys.stderr)

    ext = metadata['file_format']
    if ext in ['.jpg', '.jpeg', '.tiff', '.png']:
        metadata = extract_image_metadata(file_path, metadata)
    elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
        metadata = extract_video_metadata(file_path, metadata)
    elif ext in ['.mp3', '.flac', '.wav', '.aac']:
        metadata = extract_audio_metadata(file_path, metadata)
    else:
        print(f"Unsupported file type for file: {file_path}", file=sys.stderr)

    return metadata

def insert_metadata(conn, metadata):
    """SQLite database mein metadata insert ya update karta hai."""
    try:
        conn.execute("""
            INSERT OR REPLACE INTO media_metadata
            (file_path, file_format, resolution, duration, geolocation, file_size, date_created, date_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata['file_path'],
            metadata['file_format'],
            metadata['resolution'],
            metadata['duration'],
            metadata['geolocation'],
            metadata['file_size'],
            metadata['date_created'],
            metadata['date_modified']
        ))
        conn.commit()
    except Exception as e:
        print(f"Error inserting metadata for {metadata['file_path']}: {e}", file=sys.stderr)

def scan_directory(directory, conn):
    """
    Specified directory ko recursively scan karta hai supported multimedia files ke liye,
    metadata extract karta hai, aur results ko database mein store karta hai.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                print(f"Processing file: {file_path}")
                try:
                    metadata = extract_metadata(file_path)
                    insert_metadata(conn, metadata)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}", file=sys.stderr)
            else:
                # Unsupported file types ko skip karo
                continue

def query_database(conn, filters):
    """
    Provided filters ke basis par database ko query karta hai.
    Filters mein date range (date_created), file type, location, resolution, aur file size shamil ho sakte hain.
    """
    query = "SELECT * FROM media_metadata WHERE 1=1"
    params = []

    if filters.get('date_from') and filters.get('date_to'):
        query += " AND date_created BETWEEN ? AND ?"
        params.extend([filters['date_from'] + " 00:00:00", filters['date_to'] + " 23:59:59"])
    if filters.get('file_type'):
        query += " AND file_format = ?"
        params.append(filters['file_type'] if filters['file_type'].startswith('.') else f".{filters['file_type']}")
    if filters.get('location'):
        # Partial matches allow karne ke liye LIKE query use karo geolocation par (jaise latitude ya longitude)
        query += " AND geolocation LIKE ?"
        params.append(f"%{filters['location']}%")
    if filters.get('resolution'):
        query += " AND resolution = ?"
        params.append(filters['resolution'])
    if filters.get('min_size') is not None and filters.get('max_size') is not None:
        query += " AND file_size BETWEEN ? AND ?"
        params.extend([filters['min_size'], filters['max_size']])
    elif filters.get('min_size') is not None:
        query += " AND file_size >= ?"
        params.append(filters['min_size'])
    elif filters.get('max_size') is not None:
        query += " AND file_size <= ?"
        params.append(filters['max_size'])

    try:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error querying database: {e}", file=sys.stderr)
        return []

def print_results(rows):
    """Formatted manner mein query results print karta hai."""
    if not rows:
        print("No results found.")
        return
    for row in rows:
        print("-" * 60)
        print(f"ID: {row[0]}")
        print(f"File Path: {row[1]}")
        print(f"Format: {row[2]}")
        print(f"Resolution: {row[3]}")
        print(f"Duration: {row[4]}")
        print(f"Geolocation: {row[5]}")
        print(f"File Size: {row[6]} bytes")
        print(f"Date Created: {row[7]}")
        print(f"Date Modified: {row[8]}")
    print("-" * 60)

def main():
    # Argparse ka use karke CLI define karo with two subcommands: 'scan' aur 'query'
    parser = argparse.ArgumentParser(
        description="CLI-based multimedia metadata extractor and database organizer."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand for scanning directories aur database update karne ke liye
    scan_parser = subparsers.add_parser("scan", help="Scan directories to extract metadata")
    scan_parser.add_argument("directory", help="Directory to scan for multimedia files")
    scan_parser.add_argument("--db", default="media_metadata.db", help="Path to SQLite database file")

    # Subcommand for querying the metadata database
    query_parser = subparsers.add_parser("query", help="Query the metadata database")
    query_parser.add_argument("--db", default="media_metadata.db", help="Path to SQLite database file")
    query_parser.add_argument("--date_from", help="Start date (YYYY-MM-DD) for file creation filter")
    query_parser.add_argument("--date_to", help="End date (YYYY-MM-DD) for file creation filter")
    query_parser.add_argument("--file_type", help="Filter by file type (e.g., jpg, mp4)")
    query_parser.add_argument("--location", help="Filter by geolocation (partial match, e.g., latitude or longitude)")
    query_parser.add_argument("--resolution", help="Filter by resolution (e.g., 1920x1080)")
    query_parser.add_argument("--min_size", type=int, help="Minimum file size in bytes")
    query_parser.add_argument("--max_size", type=int, help="Maximum file size in bytes")

    args = parser.parse_args()

    # SQLite database se connect karo
    try:
        conn = sqlite3.connect(args.db)
    except Exception as e:
        print(f"Error connecting to database {args.db}: {e}", file=sys.stderr)
        sys.exit(1)

    # Agar table na ho toh create karo
    create_table(conn)

    # User input ke basis par commands process karo
    if args.command == "scan":
        # Specified directory scanning shuru karo
        if not os.path.isdir(args.directory):
            print(f"The directory {args.directory} does not exist.", file=sys.stderr)
            sys.exit(1)
        print(f"Scanning directory: {args.directory}")
        scan_directory(args.directory, conn)
        print("Scanning completed.")
    elif args.command == "query":
        # Provided CLI arguments se filters prepare karo
        filters = {
            'date_from': args.date_from,
            'date_to': args.date_to,
            'file_type': args.file_type,
            'location': args.location,
            'resolution': args.resolution,
            'min_size': args.min_size,
            'max_size': args.max_size,
        }
        print("Querying database with filters:")
        for key, value in filters.items():
            if value is not None:
                print(f"  {key}: {value}")
        results = query_database(conn, filters)
        print_results(results)
    else:
        parser.print_help()

    # Database connection close karo
    conn.close()

if __name__ == "__main__":
    main()