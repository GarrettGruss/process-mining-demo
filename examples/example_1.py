"""Basic example from the PM4PY readme"""

import pm4py
import pathlib

if __name__ == "__main__":
    working_directory = pathlib.Path().resolve()
    log = pm4py.read_xes(f"{working_directory}/examples/example_1.xes")
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log)

    # Save the Petri net visualization
    output_file = f"{working_directory}/examples/output/example_1.svg"
    pm4py.save_vis_petri_net(net, initial_marking, final_marking, str(output_file))
    print(f"Petri net saved to: {output_file}")
