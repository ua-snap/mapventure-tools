import fireventure
import argparse

# parse commandline args
parser = argparse.ArgumentParser( description='GET FIRE DATA FROM THE AICC REST SERVICES' )
parser.add_argument( '-p', '--output_directory', action='store', dest='output_directory', type=str, help='path to output directory', default='/tmp' )

args = parser.parse_args()
output_directory = args.output_directory

fireventure.run(output_directory)
