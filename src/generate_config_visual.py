import sys
from lxml import etree
import os


def print_help():
    print("usage : config_folder_path")


def main():
    number_of_args = len(sys.argv)
    parser = etree.XMLParser(remove_comments=False)
    etree.set_default_parser(parser)

    if (number_of_args < 2):
        print_help()
        exit(-1)

    folder = sys.argv[1]

    generated_configs_folder = folder

    if not os.path.exists(generated_configs_folder):
        os.makedirs(generated_configs_folder)

    tree = etree.parse(folder+"/kilobot_generic_controller.argos")
    root = tree.getroot()
    speed = "0.0"
    for params in root.iter('params'):
        # print(params.attrib)
        speed = params.get("linearvelocity", speed)

    for loop_functions in root.iter('loop_functions'):
        # print(loop_functions.attrib)
        loop_functions.set("speed", speed)

    visualization = etree.SubElement(root, "visualization")

    qt_opengl = etree.SubElement(visualization, "qt-opengl")
    camera = etree.SubElement(qt_opengl, "camera")
    placement = etree.SubElement(camera, "placement", idx="0", position="-0.616296,0.025,0.461661",
                                 look_at="0.0978462,0.025,-0.23834", up="0.700001,0,0.714142", lens_focal_length="20")

    tree.write(generated_configs_folder +
               "/kilobot_generic_controller_viz.argos", xml_declaration=True)


if __name__ == '__main__':
    main()
