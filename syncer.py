import argparse
import io
import subprocess


def fswatch(dir):
    with subprocess.Popen(['fswatch', '-r', dir], stdout=subprocess.PIPE).stdout as out:
        for line in io.TextIOWrapper(out, encoding='utf-8'):
            yield line.strip('\n')


def rsync(from_path, host, to_path, dry_run=False):
    flags = ['--archive', '--verbose']
    if dry_run:
        flags += ['--dry-run']
    cmd = ['rsync'] + flags + [from_path, '{host}:{to_path}'.format(host=host, to_path=to_path)]
    subprocess.check_call(' '.join(cmd))


def sync(watch_path, host, target_path, dry_run):
    print('Started sync')
    for file in fswatch(watch_path):
        print('Change detected in {file}'.format(file=file))
        rsync(file, host, target_path, dry_run)
    print('Sync ended')


def main():
    parser = argparse.ArgumentParser(description='Sync files from your machine to a remote host continously')
    parser.add_argument('--watch-dir', help='Path to dir to be synced. Like: /tmp/', required=True)
    parser.add_argument(
        '--host',
        help='Address of the host to be synced. Like: ctr-e138-1518143905142-552371-01-000002.hwx.site', required=True
    )
    parser.add_argument('--target-path', help='Path of the target dir to be synced. Like: /tmp', required=True)
    parser.add_argument('--user', help='User on the remote machine. Like: root', default='root')
    parser.add_argument(
        '--dry-run',
        action='store_true', help='Do not actually do anything just print what would have been done'
    )

    args = parser.parse_args()
    watch_dir = args.watch_dir
    host = '{user}@{host}'.format(user=args.user, host=args.host)
    target_path = args.target_path
    dry_run = args.dry_run

    sync(watch_dir, host, target_path, dry_run)


if __name__ == '__main__':
    main()