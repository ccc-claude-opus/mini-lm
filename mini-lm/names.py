"""英文人名與英文的寫法（gen_minilang.py、gen_world.py 共用）。"""
import re

# 256 個常見的英文名字，都在 5 個字母以內（universal.md：人名是外來語）
EN_NAMES = """Tom Amy Ben Lily Sam Lucy Jack Emma Max Anna Leo Mia Dan Kate Joe Rose Tim Ruby Ken Nina
Bob Jane Ian Zoe Ray Ivy Ted Sue Ned Fay Hal Meg Gus Joy Roy Eve Rex Pam Kim Ada Paul Mary Mark Lisa Nick Ella
Pete Judy Ryan Sara Luke Tina Adam Beth Alan Cora Andy Dora Bill Edna Carl Elsa Dave Erin Eric Gina Fred Gwen
Gary Hope Hank Iris Jake Jill Jean Joan John June Josh Kyle Lena Liam Luna Matt Mona Mike Nora Nate Olga Noah
Owen Phil Rita Rob Ruth Sean Seth Tara Toby Tess Tony Uma Troy Vera Will Wren Abby Alex Alice Ava Bart Bea Brad
Brian Carol Chad Chloe Chris Cindy Clara Cody Cole Dale Dean Diana Donna Doug Drew Dylan Eli Ellen Emily Ethan
Evan Ezra Finn Flora Frank Gail Gabe Glen Grace Greg Hanna Harry Heidi Helen Henry Holly Hugo Hugh Ida Irene
Isaac Jason Jay Jenny Jesse Joel Jonas Julia Karen Kevin Laura Leah Leon Linda Logan Lori Louis Lydia Mabel
Maria Megan Molly Oscar Paula Peter Quinn Ralph Rick Robin Ron Rosa Rudy Sally Sandy Sarah Simon Sofia Stan
Steve Susan Terry Todd Tyler Wade Walt Wanda Wendy Wes Yuri Zack Zara Al Alma Amos Asa Axel Bess Boyd Bud Burt
Cal Cara Cleo Cruz Dina Dirk Duke Earl Emil Enzo Esme Gil Igor Ines Jade Jon Kai Kira Lars Lola Mae Milo Nell
Odin Otto Pia Rhea Rory Saul Tad Theo Ugo Vic Wynn Yale Yves Zane Arlo Bree Cass Ari Bo Cy""".split()


def spaced(text):
    """universal.md 的寫法：英文和中文（或數字）之間空一格，中文標點旁邊不空。"""
    text = re.sub(r'([A-Za-z])(?=[一-鿿0-9])', r'\1 ', text)
    return re.sub(r'(?<=[一-鿿0-9])([A-Za-z])', r' \1', text)
