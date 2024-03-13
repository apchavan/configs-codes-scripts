"""
    Custom D-Tale backend service module that implements `GET` and `POST` APIs for communication.
"""

import flask
import pandas as pd

from dtale.app import build_app, DtaleFlask
from dtale.views import startup, DtaleData
from dtale.global_state import cleanup

# from constants import HOST_ADDRESS, DTALE_PORT_NO


# Create an app instance of `DtaleFlask`.
dtaleflask_app: DtaleFlask = build_app(reaper_on=False)


class _DTale_Backend:
    """
    Private class that actually stores the `DtaleData` & allows to set new data as required.
    """

    _dtale_instance_count: int = 0
    _dtale_data: DtaleData = None

    @staticmethod
    def set_data(new_df: pd.DataFrame):
        # Increment instance count before setting data.
        _DTale_Backend.set_dtale_instance_count(
            new_count=_DTale_Backend.get_instance_count() + 1,
        )

        # Set new data received in `new_df`.
        _DTale_Backend._dtale_data = startup(
            data_id=_DTale_Backend.get_instance_count(),
            data=new_df,
            ignore_duplicate=True,
        )

    @staticmethod
    def set_dtale_instance_count(new_count: int):
        """
        Set count of running `DTale` instances.
        """
        _DTale_Backend._dtale_instance_count = new_count

    @staticmethod
    def get_instance_count() -> int:
        """
        Return count of running `DTale` instances.
        """
        return _DTale_Backend._dtale_instance_count


@dtaleflask_app.route("/set_data", methods=["POST"])
def set_data():
    """
    Function for `POST`ing DataFrames to `D-Tale`.
    """
    if flask.request.method.upper() != "POST":
        return dtaleflask_app.make_response(
            rv={
                "status": 400,
                "message": f"Bad request {flask.request.method.upper()}.",
            },
        )

    if flask.request.get_json().strip() == "":
        return dtaleflask_app.make_response(
            rv={"status": 400, "message": "No DataFrame received in JSON format."},
        )

    # print(f"\n JSON -> {type(flask.request.get_json())}")

    parsed_df = pd.read_json(flask.request.get_json())
    # print(f"\n parsed_df = \n{parsed_df}\n")

    # Store the dataframe in D-Tale backend.
    _DTale_Backend.set_data(new_df=parsed_df)

    return dtaleflask_app.make_response(
        rv={
            "status": 200,
            "message": f"Successfully stored data at instance {_DTale_Backend.get_instance_count()}.",
        },
    )


@dtaleflask_app.route("/get_instance_count", methods=["GET"])
def get_instance_count():
    """
    Function for `GET`ting count of currently running instances of `D-Tale`.
    """
    if flask.request.method.upper() != "GET":
        return dtaleflask_app.make_response(
            rv={
                "status": 400,
                "message": f"Bad request {flask.request.method.upper()}.",
            },
        )

    # print(f"dtale.instances() -> ({type(dtale.instances())}) \n{dtale.instances()}")

    return dtaleflask_app.make_response(
        rv={
            "status": 200,
            "message": _DTale_Backend.get_instance_count(),
        },
    )


@dtaleflask_app.route("/cleanup_instances", methods=["GET"])
def cleanup_instances():
    """
    Function for `GET`ting count of currently running instances of `D-Tale`.

    This will likely be called from other script as a cron-job from operating system.
    """
    if flask.request.method.upper() != "GET":
        return dtaleflask_app.make_response(
            rv={
                "status": 400,
                "message": f"Bad request {flask.request.method.upper()}.",
            },
        )

    # Get a count of running DTale instances.
    dtale_instances_count: int = _DTale_Backend.get_instance_count()

    # Clean all DTale instances & the count stored in `_DTale_Backend._dtale_instance_count`.
    cleanup()
    _DTale_Backend.set_dtale_instance_count(0)

    return dtaleflask_app.make_response(
        rv={
            "status": 200,
            "message": f"Successfully clearerd {dtale_instances_count} instances.",
        },
    )


if __name__ == "__main__":
    dtaleflask_app.run(
        host=HOST_ADDRESS,  # TODO: Change this parameter.
        port=DTALE_PORT_NO,  # TODO: Change this parameter.
    )
