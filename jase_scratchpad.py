from pathlib import PurePosixPath
from pprint import pprint

from P4 import P4

# from random_word import RandomWords

TEMPLATE_DEPOT_NAME = "template"
TEMPLATE_BRANCH_VIEW = [
    '"{template_folder_path}/..." "{dev_folder_path}/..."',
    '"{template_rs_path}" "{dev_folder_path}/{new_rs_filename}"',
    '"{template_uproject_path}" "{dev_folder_path}/{new_uproject_filename}"',
]

p4 = P4()
p4.connect()


def main():
    branch_map = p4.fetch_branch("test")
    project_name = validate_input("Enter name for new project: ", lambda x: len(x) > 2)
    depot_name = create_depot(project_name)
    stream = select_stream(f"//{TEMPLATE_DEPOT_NAME}/...")
    uproject_path = select_uproject(stream)
    prod_stream_spec, dev_stream_spec = create_streams(
        depot_name, stream["Stream"], project_name
    )
    branch_map = make_branch_map(uproject_path, dev_stream_spec, project_name)
    populate_new_streams(branch_map, dev_stream_spec, project_name)
    delete_branch_map(branch_map)


def select_stream(depot_path: str):
    streams = p4.run_streams(depot_path)
    print("Select which template stream by number:")
    for i, stream in enumerate(streams):
        print(f"{i+1}: {stream['Stream']} - {stream['desc'].strip()}")
    selection = validate_input("> ", lambda x: int(x) > 0 and int(x) <= len(streams))
    return streams[int(selection) - 1]


def select_uproject(stream: dict):
    files = p4.run_files(f'{stream["Stream"]}/....uproject')
    for i, file in enumerate(files):
        print(f"{i+1}: {file['depotFile']}")
    selection = validate_input("> ", lambda x: int(x) > 0 and int(x) <= len(files))
    return files[int(selection) - 1]


def create_depot(project_name: str):
    # Get a depot-friendly name!
    depot_name = f'prj-{project_name.lower().replace(" ", "-")}'
    if depot_exists(depot_name):
        print(
            f"A depot already exists with the name {depot_name}."
            "\nEnter 'y' to use this existing depot. Anything else to abort."
        )
        resp = input("> ").strip()
        if resp == "y":
            return depot_name
        raise Exception("Aborting... Depot already exists.")
    depot = p4.fetch_depot("-t", "stream", depot_name)
    depot["Description"] = f"The depot for Project {project_name}."
    p4.save_depot(depot)

    # Get a depot-friendly name!
    print(f"Depot {depot_name} successfully created!")
    return depot_name


def depot_exists(depot_name):
    return depot_name.lower() in [depot["name"].lower() for depot in p4.run_depots()]


def create_streams(depot_name: str, template_stream: str, project_name: str):
    prod_stream_spec = create_mainline_stream(
        depot_name, template_stream, "prod", project_name
    )
    dev_stream_spec = create_development_stream(
        depot_name, prod_stream_spec, "dev", project_name
    )
    return prod_stream_spec, dev_stream_spec


def create_mainline_stream(
    depot_name: str, from_stream: str, stream_name: str, project_name: str
):
    from_stream_spec = p4.run_stream("-o", from_stream)[0]
    new_stream_spec = p4.fetch_stream(f"//{depot_name}/{stream_name}")
    new_stream_spec["Type"] = "mainline"
    new_stream_spec["Paths"] = from_stream_spec["Paths"]
    new_stream_spec["Ignored"] = from_stream_spec.get("Ignored", [])
    new_stream_spec["Remapped"] = from_stream_spec.get("Remapped", [])
    new_stream_spec[
        "Description"
    ] = f"The production stream for Project {project_name}."
    p4.save_stream(new_stream_spec)
    print(f"Created stream {new_stream_spec['Name']} at {new_stream_spec['Stream']}")
    return new_stream_spec


def create_development_stream(
    depot_name: str, parent_stream: dict, stream_name: str, project_name: str
):
    new_stream_spec = p4.fetch_stream(f"//{depot_name}/{stream_name}")
    new_stream_spec["Parent"] = parent_stream["Stream"]
    new_stream_spec[
        "Description"
    ] = f"The development stream for Project {project_name}."
    p4.save_stream(new_stream_spec)
    print(f"Created stream {new_stream_spec['Name']} at {new_stream_spec['Stream']}")
    return new_stream_spec


def make_branch_map(
    template_project: dict,
    development_stream: dict,
    project_name: str,
):
    branch_map = p4.fetch_branch(f"branch_map_{project_name.lower().replace(' ', '_')}")
    # first is just the folder name
    template_uproject_path = PurePosixPath(template_project["depotFile"])
    template_folder_path = template_uproject_path.parent
    template_rs_path = (
        f"{template_uproject_path.parent}/rs_{template_uproject_path.stem.lower()}.json"
    )
    dev_folder_path = f'{development_stream["Stream"]}/Project {project_name}'
    new_uproject_filename = f'Project_{project_name.replace(" ", "_")}.uproject'
    new_rs_filename = f'rs_project_{project_name.lower().replace(" ", "_")}.json'

    branch_map["View"] = [
        view.format(
            template_folder_path=template_folder_path,
            dev_folder_path=dev_folder_path,
            template_rs_path=template_rs_path,
            template_uproject_path=template_uproject_path,
            new_rs_filename=new_rs_filename,
            new_uproject_filename=new_uproject_filename,
        )
        for view in TEMPLATE_BRANCH_VIEW
    ]

    p4.save_branch(branch_map)
    print(f"Created branch map {branch_map['Branch']}")
    return branch_map["Branch"]


def delete_branch_map(branch_map: str):
    p4.run_branch("-d", branch_map)
    print(f"Deleted branch mapping {branch_map}")


def populate_new_streams(branch_map, dev_stream_spec, project_name):
    print(
        f"Populating with initial template for Project {project_name} into dev stream..."
    )
    p4.run_populate(
        "-d",
        f"Populating with initial template for Project {project_name} into dev stream",
        "-b",
        branch_map,
    )
    print(
        f"Populating with initial template for Project {project_name} into prod stream..."
    )
    p4.run_populate(
        "-d", "Populating prod stream from dev stream", "-S", dev_stream_spec["Stream"]
    )


def validate_input(prompt: str, validation_function=lambda x: True):
    while True:
        resp = input(prompt)
        try:
            if validation_function(resp):
                return resp
        except Exception as e:
            print("Invalid input: ", e)


if __name__ == "__main__":
    main()
