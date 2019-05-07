"""Test the main CanSen module."""

from cansen.cansen import main


def test_one_complete_simulation(datadir, capsys):
    """Run an integration/regression test of one simulation."""
    input_file = datadir / "test_one_complete_simulation.inp"
    chem_file = datadir / "gri30.xml"
    save_file = datadir / "save.hdf"
    output_file = datadir / "output.out"
    main(
        input_filename=str(input_file),
        mech_filename=str(chem_file),
        save_filename=str(save_file),
        output_filename=str(output_file),
    )
    assert output_file.is_file()
    captured = capsys.readouterr()
    assert output_file.read_text() == captured.out


def test_multi_simulation(datadir):
    """Run an integration/regression test of multiple simulations."""
    input_file = datadir / "test_multi_simulation.inp"
    chem_file = datadir / "gri30.xml"
    chem_file = datadir / "gri30.xml"
    save_file = datadir / "save.hdf"
    output_file = datadir / "output.out"
    main(
        input_filename=str(input_file),
        mech_filename=str(chem_file),
        save_filename=str(save_file),
        output_filename=str(output_file),
        multi=1,
    )
    assert output_file.is_file()
