import sys
from lxml import etree
import os


def print_help():
    print("usage : config_folder_path, numberOfRobots, alpha, rho, speed")


def main():
    number_of_args = len(sys.argv)
    parser = etree.XMLParser(remove_comments=False)
    etree.set_default_parser(parser)

    if (number_of_args < 6):
        print_help()
        exit(-1)

    folder = sys.argv[1]
    numberofrobots = int(sys.argv[2])
    alpha = float(sys.argv[3])
    rho = float(sys.argv[4])
    arena_radius = float(sys.argv[5])
    generated_configs_folder = folder + "/generated_configs"

    if not os.path.exists(generated_configs_folder):
        os.makedirs(generated_configs_folder)

    tree = etree.parse(folder+"/kilobot_generic_controller.argos")
    root = tree.getroot()

    for params in root.iter('params'):
        # print(params.attrib)
        if(params.get("behavior") == "build/behaviors_simulation/CRWLEVY_2.0_0.90"):
            params.set("behavior", "build/behaviors_simulation/CRWLEVY_" +
                       "%.1f_" % alpha + "%.2f" % rho)
        if(params.get("arena_radius")):
            params.set("arena_radius", "%.3f" % arena_radius)

    for loop_functions in root.iter('loop_functions'):
        # print(loop_functions.attrib)
        loop_functions.set("alpha", "%.1f" % alpha)
        loop_functions.set("rho", "%.2f" % rho)
        loop_functions.set("num_robots", "%d" % numberofrobots)
        loop_functions.set("arena_radius", "%.3f" % arena_radius)

    tree.write(generated_configs_folder + "/kilobot_sim_%.3f_%d_%.1f_%.2f.argos" %
               (arena_radius, numberofrobots, alpha, rho), xml_declaration=True)

    comments = tree.xpath('//comment()')

    for c in comments:
        p = c.getparent()
        p.remove(c)


if __name__ == '__main__':
    main()
