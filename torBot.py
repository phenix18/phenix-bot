"""
MAIN MODULE
"""
import argparse

from requests.exceptions import HTTPError

from modules.analyzer import LinkTree
from modules.color import color
from modules.link_io import LinkIO
from modules.link import LinkNode
from modules.updater import updateTor
from modules.savefile import saveJson
from modules.info import execute_all
from modules.wsserver import start_wsserver

# GLOBAL CONSTS
LOCALHOST = "127.0.0.1"
DEFPORT = 9050

# TorBot VERSION
__VERSION = "1.3.1"

def header():
    """
    Prints out header ASCII art
    """
    license_msg = color("LICENSE: GNU Public License", "red")
    banner = r"""
                           __  ____  ____  __        ______
                          / /_/ __ \/ __ \/ /_  ____/_  __/
                         / __/ / / / /_/ / __ \/ __ \/ /
                        / /_/ /_/ / _, _/ /_/ / /_/ / /
                        \__/\____/_/ |_/_____/\____/_/  V{VERSION}
              """.format(VERSION=__VERSION)
    banner = color(banner, "red")

    title = r"""
                                    {banner}
                    #######################################################
                    #  TorBot - An OSINT Tool for Deep Web                #
                    #  GitHub : https://github.com/DedsecInside/TorBot    #
                    #  Help : use -h for help text                        #
                    #######################################################
                                  {license_msg} 
              """

    title = title.format(license_msg=license_msg, banner=banner)
    print(title)


def get_args():
    """
    Parses user flags passed to TorBot
    """
    parser = argparse.ArgumentParser(prog="TorBot",
                                     usage="Gather and analayze data from Tor sites.")
    parser.add_argument("--version", action="store_true",
                        help="Show current version of TorBot.")
    parser.add_argument("--update", action="store_true",
                        help="Update TorBot to the latest stable version")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-u", "--url", help="Specifiy a website link to crawl")
    parser.add_argument("--ip", help="Change default ip of tor")
    parser.add_argument("-p", "--port", help="Change default port of tor")
    parser.add_argument("-s", "--save", action="store_true",
                        help="Save results in a file")
    parser.add_argument("-m", "--mail", action="store_true",
                        help="Get e-mail addresses from the crawled sites")
    parser.add_argument("-e", "--extension", action='append', dest='extension',
                        default=[],
                        help=' '.join(("Specifiy additional website",
                                       "extensions to the list(.com , .org, .etc)")))
    parser.add_argument("-i", "--info", action="store_true",
                        help=' '.join(("Info displays basic info of the",
                                       "scanned site")))
    parser.add_argument("-v", "--visualize", action="store_true",
                        help="Visualizes tree of data gathered.")
    parser.add_argument("-d", "--download", action="store_true",
                        help="Downloads tree of data gathered.")
    parser.add_argument("--server", action="store_true",
                        help="Start TorBot WebSocket server.")
    return parser.parse_args()


def main():
    """
    TorBot's Core
    """
    args = get_args()
    if args.server:
        start_wsserver()

    # If flag is -v, --update, -q/--quiet then user only runs that operation
    # because these are single flags only
    if args.version:
        print("TorBot Version:" + __VERSION)
        exit()
    if args.update:
        updateTor()
        exit()
    if not args.quiet:
        header()
    try:
        node = LinkNode(args.url, tld=args.extension)
    except (ValueError, HTTPError, ConnectionError) as err:
        raise err
    # If url flag is set then check for accompanying flag set. Only one
    # additional flag can be set with -u/--url flag
    if args.url:
        try:
            node = LinkNode(args.url)
        except (ValueError, HTTPError, ConnectionError) as err:
            raise err
        LinkIO.display_ip()
        # -m/--mail
        if args.mail:
            print(node.emails)
            if args.save:
                saveJson('Emails', node.emails)
        # -i/--info
        elif args.info:
            execute_all(node.uri)
            if args.save:
                print('Nothing to save.\n')
        elif args.visualize:
            tree = LinkTree(node)
            tree.show()
        elif args.download:
            tree = LinkTree(node)
            file_name = str(input("File Name (.pdf/.png/.svg): "))
            tree.save(file_name)
        else:
            LinkIO.display_children(node)
            if args.save:
                saveJson("Links", node.links)
    else:
        print("usage: See torBot.py -h for possible arguments.")

    print("\n\n")


if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
