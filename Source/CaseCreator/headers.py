"""
/*--------------------------------*- C++ -*----------------------------------*\
-------------------------------------------------------------------------------
 *****   ******   *          ***     *****   *     *  
*     *  *     *  *         *   *   *     *  *     *  
*        *     *  *        *     *  *        *     *  
 *****   ******   *        *******   *****   *******  
      *  *        *        *     *        *  *     *  
*     *  *        *        *     *  *     *  *     *  
 *****   *        *******  *     *   *****   *     *  
-------------------------------------------------------------------------------
 * SplashCaseCreator is part of Splash CFD automation tool.
 * Copyright (c) 2024 THAW TAR
 * Copyright (c) 2025 Mohamed Aly Sayed and Thaw Tar
 * All rights reserved.
 *
 * This software is licensed under the GNU Lesser General Public License version 3 (LGPL-3.0).
 * You may obtain a copy of the license at https://www.gnu.org/licenses/lgpl-3.0.en.html
 */
"""

letters = {
    'a': [
        "  ***  ",
        " *   * ",
        "*     *",
        "*******",
        "*     *",
        "*     *",
        "*     *"
    ],
    'b': [
        "****** ",
        "*     *",
        "*     *",
        "****** ",
        "*     *",
        "*     *",
        "****** "
    ],
    'c': [
        " ***** ",
        "*     *",
        "*      ",
        "*      ",
        "*      ",
        "*     *",
        " ***** "
    ],
    'd': [
        "****** ",
        "*     *",
        "*     *",
        "*     *",
        "*     *",
        "*     *",
        "****** "
    ],
    'e': [
        "*******",
        "*      ",
        "*      ",
        "****   ",
        "*      ",
        "*      ",
        "*******"
    ],
    'f': [
        "*******",
        "*      ",
        "*      ",
        "****   ",
        "*      ",
        "*      ",
        "*      "
    ],
    'g': [
        " ***** ",
        "*     *",
        "*      ",
        "*  ****",
        "*     *",
        "*     *",
        " ***** "
    ],
    'h': [
        "*     *",
        "*     *",
        "*     *",
        "*******",
        "*     *",
        "*     *",
        "*     *"
    ],
    'i': [
        "*******",
        "   *   ",
        "   *   ",
        "   *   ",
        "   *   ",
        "   *   ",
        "*******"
    ],
    'j': [
        "*******",
        "    *  ",
        "    *  ",
        "    *  ",
        "*   *  ",
        "*   *  ",
        " ***   "
    ],
    'k': [
        "*     *",
        "*    * ",
        "*   *  ",
        "****   ",
        "*   *  ",
        "*    * ",
        "*     *"
    ],
    'l': [
        "*      ",
        "*      ",
        "*      ",
        "*      ",
        "*      ",
        "*      ",
        "*******"
    ],
    'm': [
        "*     *",
        "**   **",
        "* * * *",
        "*  *  *",
        "*     *",
        "*     *",
        "*     *"
    ],
    'n': [
        "*     *",
        "**    *",
        "* *   *",
        "*  *  *",
        "*   * *",
        "*    **",
        "*     *"
    ],
    'o': [
        " ***** ",
        "*     *",
        "*     *",
        "*     *",
        "*     *",
        "*     *",
        " ***** "
    ],
    'p': [
        "****** ",
        "*     *",
        "*     *",
        "****** ",
        "*      ",
        "*      ",
        "*      "
    ],
    'q': [
        " ***** ",
        "*     *",
        "*     *",
        "*     *",
        "*   * *",
        "*    * ",
        " **** *"
    ],
    'r': [
        "****** ",
        "*     *",
        "*     *",
        "****** ",
        "*   *  ",
        "*    * ",
        "*     *"
    ],
    's': [
        " ***** ",
        "*     *",
        "*      ",
        " ***** ",
        "      *",
        "*     *",
        " ***** "
    ],
    't': [
        "*******",
        "   *   ",
        "   *   ",
        "   *   ",
        "   *   ",
        "   *   ",
        "   *   "
    ],
    'u': [
        "*     *",
        "*     *",
        "*     *",
        "*     *",
        "*     *",
        "*     *",
        " ***** "
    ],
    'v': [
        "*     *",
        "*     *",
        "*     *",
        "*     *",
        " *   * ",
        "  * *  ",
        "   *   "
    ],
    'w': [
        "*     *",
        "*     *",
        "*     *",
        "*  *  *",
        "* * * *",
        "**   **",
        "*     *"
    ],
    'x': [
        "*     *",
        " *   * ",
        "  * *  ",
        "   *   ",
        "  * *  ",
        " *   * ",
        "*     *"
    ],
    'y': [
        "*     *",
        " *   * ",
        "  * *  ",
        "   *   ",
        "   *   ",
        "   *   ",
        "   *   "
    ],
    'z': [
        "*******",
        "     * ",
        "    *  ",
        "   *   ",
        "  *    ",
        " *     ",
        "*******"
    ]
}
    
def print_word(word):
    for i in range(7):
        for letter in word:
            print(letters[letter][i], end="  ")
        print()

def get_word(word):
    output = ""
    for i in range(7):
        for letter in word:
            #print(letters[letter][i], end="  ")
            output += letters[letter][i] + "  "
        output += "\n"
    return output

def get_SplashCaseCreator_header():
    word = get_word("splash") # Changed from "SplashCaseCreator"
    output = "-------------------------------------------------------------------------------\n"
    output += word
    output += "-------------------------------------------------------------------------------\n"
    return output


if __name__ == '__main__':
    output = "-------------------------------------------------------------------------------\n"
    output += get_SplashCaseCreator_header()
    output += "-------------------------------------------------------------------------------\n"
    print(output)