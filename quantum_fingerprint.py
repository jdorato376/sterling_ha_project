"""Generate a minimal CycloneDX SBOM from ``requirements.txt``."""

from pathlib import Path
from typing import List

from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.output import get_instance, OutputFormat


def _parse_requirements(path: Path) -> List[Component]:
    components: List[Component] = []
    if not path.exists():
        return components
    for line in path.read_text().splitlines():
        pkg = line.strip()
        if not pkg or pkg.startswith("#"):
            continue
        if "==" in pkg:
            name, version = pkg.split("==", 1)
        else:
            name, version = pkg, "latest"
        components.append(
            Component(name=name, version=version, component_type=ComponentType.LIBRARY)
        )
    return components


def generate_sbom(output_path: str = "sbom.json") -> str:
    bom = Bom()
    req_file = Path("requirements.txt")
    for comp in _parse_requirements(req_file):
        bom.add_component(comp)
    outputter = get_instance(bom=bom, output_format=OutputFormat.JSON)
    outputter.output_to_file(filename=output_path, allow_overwrite=True)
    return output_path


if __name__ == "__main__":
    import sys

    path = generate_sbom(sys.argv[1] if len(sys.argv) > 1 else "sbom.json")
    print(f"SBOM written to {path}")
