from model import Notice


def preview(notice: Notice) -> str:
    return notice.subject + "\n" + notice.body
