#!/usr/bin/env python
import re
import web

web_prefix = "http://www.mcgill.ca/global/php/coursepopup.php?Course="
usage = "Usage: .courseinfo department number"
lookup = re.compile("^((?:[a-z]{4})?)\s?(\d{3})$", re.I)


def get_data(tag_class, bytes, start=0):
    """ Why don't they do this by id :( """
    look = '"'.join(("class=", tag_class, ""))
    class_index = bytes.find(look, start)
    if class_index == -1:
        return False
    tag_index = bytes.rindex("<", start, class_index)  # find the tag with this class
    tag = bytes[tag_index + 1: bytes.index(" ", tag_index)]  # name of the tag we're looking for
    data = bytes[bytes.index(">", tag_index) + 1: bytes.index("</" + tag + ">", tag_index)]
    return re.sub("<[^>]*>", "", data)


def courseinfo(phenny, input):
    """ Get information about a course at McGill by course number. If no department is specified, checks the COMP, then MATH departments. """
    query = input.group(2)
    if not query:
        return phenny.reply(usage)
    mat = lookup.match(query)
    if not mat:
        return phenny.reply(usage)
    search = mat.groups()
    for search in (
            zip(("COMP", "MATH"), (search[1], ) * 2)
            if search[0] == ""
            else [search]):  # if department not provided assume COMP, then MATH
        url = web_prefix + '+'.join(search)
        bytes = web.get(url)
        title = get_data("course_title", bytes)
        if title:
            break
    if not title:
        return phenny.reply("Sorry, no description available for course number " + query + " for the academic year.  " + url)
    credits = get_data("course_credits", bytes)
    number = get_data("course_number", bytes)  # maybe wasteful, but who knows maybe there's a redirect
    desc = get_data("course_description", bytes)
    phenny.say(number + ": \x02" + title + "\x02 (" + credits + ")")
    phenny.say(desc)
    phenny.say(url)
courseinfo.commands = ["courseinfo"]
courseinfo.example = usage.partition(" ")[2]
