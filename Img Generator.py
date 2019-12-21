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
    for i in ["close_active", "close_pressed", "close", "addnew", "hammer", "draw_tool2", "move_tool", "grid_mode",
              "border_mode", "border", "tile_layer", "deco_layer", "collision_layer", "loading_layer", "light_layer"]:
        print(i + ": ")
        with open("Images/" + i + ".gif", "rb") as f:
            print(base64.encodebytes(f.read()))


if __name__ == "__main__":
    main()
