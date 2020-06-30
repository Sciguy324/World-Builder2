import base64


def export():
    with open("Image/test.gif", "wb") as f:
        encoded_img = base64.decodebytes(b'''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                ''')
        f.write(encoded_img)

    with open("Image/test2.gif", "wb") as f:
        encoded_img2 = base64.decodebytes(b'''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                ''')
        f.write(encoded_img2)

    with open("Image/test3.gif", "wb") as f:
        encoded_img3 = base64.decodebytes(b'''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                ''')
        f.write(encoded_img3)


def main():
    images = {"": ["close_active", "close_pressed", "close", "addnew", "hammer", "draw_tool2", "move_tool", "grid_mode",
                   "border_mode", "border", "solidify", "desolidify", "elevate", "descend"],
              "layer/": ["tile_layer", "deco_layer", "collision_layer", "height_layer", "loading_layer", "light_layer"],
              "loading_zone/": ["delete_loading_zone", "new_loading_zone", "configure_loading_zone",
                                "copy_loading_zone", "paste_loading_zone", "extend_loading_zone", "active_loading_zone",
                                "inactive_loading_zone"],
              "lights/": ["active_light", "inactive_light", "edit_light", "new_light"]
              }
    for i, j in images.items():
        for k in j:
            print(i + k + ":")
            with open("Images/" + i + k + ".gif", "rb") as f:
                print(base64.encodebytes(f.read()))

    with open("Images/hammer.ico", "rb") as f:
        print("Icon:\n", base64.encodebytes(f.read()))


if __name__ == "__main__":
    main()
