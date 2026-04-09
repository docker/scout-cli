import subprocess

def test_docker_scout_installed():
    result = subprocess.run(
        ["docker", "scout", "version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_docker_scout_quickview():
    result = subprocess.run(
        ["docker", "scout", "quickview", "alpine"],
        capture_output=True,
        text=True
    )
    assert "Target" in result.stdout