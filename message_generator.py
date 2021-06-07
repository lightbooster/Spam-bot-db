def create_replies_string(replies, max_replies=3):
    review_format_string = "«{class_name}» - {comment}"
    review_string = ""
    if max_replies is not None:
        replies = replies[:max_replies]
    for review in replies:
        review_string += review_format_string.format(**{'class_name': review[0], 'comment': review[1]})
        review_string += '\n'
    return review_string[:-1]


def create_attention_message(number: str, common_class: str, all_classes_list: str,
                             reviews_number: int, replies: list):
    replies_string = create_replies_string(replies)
    out = \
        """
❗️ Attention! ❗️
{number} is defined as {class}! 🚫
There are also other mentioned negative activities:
{all_classes_list}

We have {reviews_number} replies 📩 :
{replies}

Want to reply bad experience with {number}? 🤬
Click on «Reply» button!
""".format(**{'number': number, 'class': common_class, 'all_classes_list': all_classes_list,
              'reviews_number': reviews_number, 'replies': replies_string})
    return out


def create_ok_message(number: str):
    out = \
        """
There is no information about {number} in our database! 
But still be careful and pay attention to people on the line.  👀

Want to reply bad experience with {number}? 🤬
Click on «Reply» button!
""".format(number=number)
    return out


def create_need_comment_string():
    out = \
        """
Please enter comments about this number 📝.
Try to describe your experience
""".format()
    return out


def create_thank_reply_string():
    out = \
        """
Thank you for committing a reply! 😉
You make our community better!
"""
    return out


def create_thank_update_string():
    out = \
        """
Your reply has been updated! ♻️ 
You make our community better!
"""
    return out


def create_default_string():
    return "Just type the number and I’ll check it!"

def create_choose_class_string():
    out = \
        """
    Please, try to choose the category 🔍
    of bad experience you had with this number.
    """
    return out


def create_hi_string():
    out1 = \
        """
Hi! ✋
My name is Spamy. 
I will tell you about strange phone numbers that called you. 🤙
"""
    out2 = create_default_string()
    return out1, out2


# number = '89107991200'
# common_class = 'Fraud'
# all_classes_list = ('Ads', 'Fraud')
# all_classes_list = ', '.join(all_classes_list)
# reviews_number = 1
#
# print(create_attention_message(number, common_class, all_classes_list, reviews_number, reviews))
# print()
# print(create_ok_message(number))