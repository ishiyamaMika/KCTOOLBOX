#-*-coding: utf-*-
import os
import sys

mod = "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])

if not mod in sys.path:
    sys.path.append(mod)


def load():
    import sentry_sdk
    def _strip_sensitive_data(event, hint):
        """
        before_send内ではset_tagできない？
        """
        # modify event here
        print
        print 
        print "-------------------------------------"
        for value in event["exception"]["values"]:
            print "..."
            for each in value.get("stacktrace", {}).get("frames", []):
                print "_____"
                path = each.get("abs_path")
                if not path:
                    continue

                path_s = path.split("python")
                if len(path_s) == 1:
                    continue

                path_ss = [l for l in path_s[1].split("\\") if l != ""]
                print "==+++", path_ss, "{}|{}".format(path_ss[0], path_ss[-1])
                # sentry_sdk.set_tag("errorType", "{}/{}".format(path_ss[0], path_ss[-1]))
                # sentry_sdk.set_tag("errorType", "test")

                # print dir(sentry_sdk)


        return event




    sentry_sdk.init(
        "https://f495f5f65a664494b9aaff767d953fd6@o1015035.ingest.sentry.io/6049616",
        traces_sample_rate=1.0,
        before_send=_strip_sensitive_data
    )

    sentry_sdk.set_tag(
        "user_name", os.environ.get("KEICA_USERNAME", os.environ["USERNAME"])
    )

if __name__ == "__main__":
    load()
