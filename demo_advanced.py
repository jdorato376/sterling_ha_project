import json
import os
from advanced_phases import (
    QuantumFingerprint,
    PlatinumConcord,
    DepartmentalAgent,
    AdaptiveSynapseRouter,
    AutonomousRepairAgent,
    DecentralizedBackupManager,
)


def main():
    # prepare a dummy file
    with open("dummy_artifact.py", "w") as f:
        f.write("print('hello')\n")

    qf = QuantumFingerprint("dummy_artifact.py", "1.0.0")
    fingerprint = qf.mint()
    print("Quantum Fingerprint:\n", json.dumps(fingerprint, indent=2))
    print("SBOM detail:\n", fingerprint["sbom"])

    concord = PlatinumConcord()
    it_agent = DepartmentalAgent("IT-01", "IT")
    hr_agent = DepartmentalAgent("HR-01", "HR")
    concord.register_agent(it_agent)
    concord.register_agent(hr_agent)
    concord.submit_task("IT-01", "Provision VM")
    concord.submit_task("HR-01", "Onboard new hire")
    concord.arbitrate_and_dispatch()
    concord.arbitrate_and_dispatch()
    print("Audit log:", json.dumps(concord.audit_log, indent=2))

    router = AdaptiveSynapseRouter()
    for q in ["time?", "translate hello", "analyze long text" * 20]:
        print(router.route_query(q))
    print("Total cost", router.cost_tracker)

    repair_agent = AutonomousRepairAgent()
    buggy_code = "def add(a, b): return a - b"
    result = repair_agent.execute_repair_cycle(buggy_code, "expected addition")
    print("Repair result:", json.dumps(result, indent=2))

    backup_mgr = DecentralizedBackupManager()
    backup_path = backup_mgr.backup_file("dummy_artifact.py")
    print("Backup created at", backup_path)


if __name__ == "__main__":
    main()
