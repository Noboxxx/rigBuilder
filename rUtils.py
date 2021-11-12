class RSide(object):
    left = 'L'
    right = 'R'
    center = 'C'

    mirrorTable = {
        left: right,
        right: left,
        center: None
    }


class RColor(object):
    yellow = 'yellow'
    red = 'red'
    lime = 'green'

    mirrorTable = {
        red: lime,
        lime: red,
        yellow: None
    }
