from flask import Blueprint, request


blueprint = Blueprint('util_service', __name__)



@blueprint.route("/headers/", methods=['GET'])
def test_show_header():
    res = [ '<html><head><title>HTTP Header</title></head><body><table border="1"><tr>' ]

    tbl = []
    for key, val in request.headers.iteritems():
        tbl.append("<th>%s</th><td>%s</td>" % ( key, val ))
        
    res.append('</tr><tr>'.join(tbl))
    res.append('</tr></table></body></html>')
    return '\n'.join(res)
