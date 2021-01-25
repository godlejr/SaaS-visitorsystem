import sys

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import backref

db = SQLAlchemy()


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def del_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs)
    if instance.first():
        instance.delete()
    else:
        instance = model(**kwargs)
        session.add(instance)
    session.commit()


class BaseMixin(object):
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # created_at = db.Column(db.DateTime, default=db.func.now())
    # updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    use_yn = db.Column(db.String(1))
    created_at = db.Column(db.DateTime, default=db.func.now())
    created_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    updated_by = db.Column(db.String(50))
    end_at = db.Column(db.DateTime, default=db.func.now())

    @hybrid_property
    def created_date(self):
        return self.created_at.strftime('%Y-%m-%d')

    @hybrid_property
    def updated_date(self):
        return self.updated_at.strftime('%Y-%m-%d')

    @hybrid_method
    def get_id(self):
        return self.id


class User(db.Model, BaseMixin):
    """사용자 계정 정보

    :param str email: Email 주소 사용자 ID로 사용
    :param str password: 암호화된 패스워드
    """
    __tablename__ = 'users'

    name = db.Column(db.Unicode(255), nullable=False)
    email = db.Column(db.Unicode(255), nullable=False, unique=True)
    password = db.Column(db.Unicode(255), nullable=False)
    authenticated = db.Column(db.Boolean, default=1)
    accesscode = db.Column(db.Unicode(255), nullable=False, unique=True)
    level = db.Column(db.Integer)
    cover = db.Column(db.Unicode(255), default='cover.jpg', nullable=False)
    avatar = db.Column(db.Unicode(255), default='avatar.png', nullable=False)

    follow = db.relationship('Follow', back_populates='user')

    @hybrid_property
    def is_admin(self):
        return True if self.level == 9 else False

    @hybrid_property
    def is_pro(self):
        return True if self.level == 2 else False

    @hybrid_property
    def is_authenticated(self):
        """Email 인증 여부 확인"""
        return True if self.authenticated else False

    @hybrid_property
    def avatar_url(self):
        return ''.join(
            (current_app.config['S3_BUCKET_NAME'], current_app.config['S3_USER_DIRECTORY'], '%s')) % self.avatar

    @hybrid_method
    def follow_check(self, session_id, follow_id):
        return Follow.query.filter_by(user_id=session_id).filter_by(follow_id=follow_id).first()

    @hybrid_method
    def following_count(self, user_id):
        return Follow.query.filter_by(user_id=user_id).count()

    @hybrid_method
    def follower_count(self, user_id):
        return Follow.query.filter_by(follow_id=user_id).count()

    @hybrid_method
    def follow_user(self, id):
        return User.query.filter(User.id == id).first()

    def __repr__(self):
        return "%s(%s)" % (self.name, self.email)


class Category(db.Model, BaseMixin):
    """카테고리 정보"""
    __tablename__ = 'categories'

    name = db.Column(db.Unicode(50), nullable=False)

    def __repr__(self):
        return self.name

    @hybrid_method
    def get_count(self, category_id):
        count = Magazine.query.filter(Magazine.category_id == category_id).count()
        return count


class Business(db.Model, BaseMixin):
    """업종 정보"""
    __tablename__ = 'businesses'

    name = db.Column(db.Unicode(50), nullable=False)

    def __repr__(self):
        return self.name


class Sido(db.Model, BaseMixin):
    """시/도 정보"""
    __tablename__ = 'sidos'

    area_id = db.Column(db.Integer, nullable=False)
    sido_code = db.Column(db.Unicode(2), nullable=False)
    name = db.Column(db.Unicode(50), nullable=False)

    def __repr__(self):
        return self.sido_code


class Follow(db.Model, BaseMixin):
    """팔로우 정보"""
    __tablename__ = 'follows'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    follow_id = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='follow')


class Residence(db.Model, BaseMixin):
    """거주지 정보"""
    __tablename__ = 'residences'

    name = db.Column(db.Unicode(50), nullable=False)


class Room(db.Model, BaseMixin):
    """공간 정보"""
    __tablename__ = 'rooms'

    name = db.Column(db.Unicode(50), nullable=False)

    @hybrid_method
    def get_count(self, room_id):
        count = Photo.query.filter(Photo.room_id == room_id).count()
        return count


class Comment(db.Model, BaseMixin):
    """댓글 내역"""
    __tablename__ = 'comments'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer)
    depth = db.Column(db.Integer, default=0)
    sort = db.Column(db.Integer, default=0)
    deleted = db.Column(db.Boolean, default=0)
    content = db.Column(db.Text)

    user = db.relationship('User', backref=backref('user_comments'))
    photos = db.relationship('PhotoComment', back_populates='comment')
    magazines = db.relationship('MagazineComment', back_populates='comment')

    @hybrid_property
    def max1_group_id(self):
        group_id = db.session.query(func.max(Comment.group_id)).one()[0]
        return (group_id + 1) if group_id else 1

    @hybrid_property
    def is_deleted(self):
        return self.deleted

    @hybrid_property
    def reply_count(self):
        if self.depth == 0:
            return db.session.query(Comment).filter(Comment.group_id == self.group_id).filter(
                Comment.depth != 0).filter(Comment.deleted != 1).count()
        return 0

    @hybrid_property
    def get_id(self):
        return self.id

    @hybrid_method
    def get_parent_id(self, group_id):
        return db.session.query(Comment).filter(Comment.group_id == group_id).filter(Comment.depth == 0).first().id


class File(db.Model, BaseMixin):
    """파일 정보"""
    __tablename__ = 'files'

    type = db.Column(db.Integer, nullable=False, default=1)
    cid = db.Column(db.Unicode(50))
    name = db.Column(db.Unicode(255), nullable=False)
    ext = db.Column(db.Unicode(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)

    @hybrid_property
    def is_photo(self):
        return True if self.type == 1 else False

    @hybrid_property
    def is_vr(self):
        return True if self.type == 2 else False

    @hybrid_property
    def is_mov(self):
        return True if self.type == 3 else False

    @hybrid_property
    def is_youtube(self):
        return True if self.type == 3 and self.cid else False

    @hybrid_property
    def youtube_url(self):
        return 'https://www.youtube.com/embed/%s' % self.cid if self.cid else None

    @hybrid_property
    def youtube_thumb_url(self):
        return 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % self.cid if self.cid else None

    @hybrid_property
    def photo_url(self):
        return 'http://static.inotone.co.kr/data/img/%s' % self.name if self.name else None

    @hybrid_property
    def photo_thumb_url(self):
        return 'http://static.inotone.co.kr/data/img/%s' % self.name if self.name else None

    @hybrid_property
    def thumb_url(self):
        return self.youtube_thumb_url if self.is_youtube else self.photo_thumb_url

    @hybrid_property
    def url(self):
        return self.youtube_url if self.is_youtube else self.photo_url

    def __repr__(self):
        return Markup('<img src="http://static.inotone.co.kr/data/img/%s" width="100" height="100">') % self.name


class Photo(db.Model, BaseMixin):
    """사진 정보"""
    __tablename__ = 'photos'

    content = db.Column(db.Text)
    hits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    magazine_id = db.Column(db.Integer, db.ForeignKey('magazines.id'))

    user = db.relationship('User', backref=backref('user_photos'))
    room = db.relationship('Room', backref=backref('room_photos'))
    file = db.relationship('File', backref=backref('file_photos'))
    magazine = db.relationship('Magazine', back_populates='photos')
    comments = db.relationship('PhotoComment', back_populates='photo')

    @hybrid_property
    def is_photo(self):
        return True if not self.file or self.file.is_photo else False

    @hybrid_property
    def is_vr(self):
        return self.file.is_vr

    @hybrid_property
    def is_mov(self):
        return self.file.is_mov

    @hybrid_property
    def is_youtube(self):
        return self.file.is_youtube

    @hybrid_property
    def thumb_url(self):
        return self.file.thumb_url

    @hybrid_property
    def youtube_url(self):
        return self.file.youtube_url

    @hybrid_property
    def file_url(self):
        return self.file.url

    @hybrid_method
    def is_active(self, model, user_id):
        return getattr(sys.modules[__name__], model).query.filter_by(photo_id=self.id, user_id=user_id).first()

    def __repr__(self):
        return "%s-%s" % (self.magazine.title, self.id)


class PhotoLike(db.Model, BaseMixin):
    """포토-좋아요 연결고리"""
    __tablename__ = 'photo_likes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))

    user = db.relationship('User', backref=backref('like_users'))
    photo = db.relationship('Photo', backref=backref('like_photos', cascade='all,delete'))


class PhotoScrap(db.Model, BaseMixin):
    """포토-좋아요 연결고리"""
    __tablename__ = 'photo_scraps'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))

    user = db.relationship('User', backref='scrap_users')
    photo = db.relationship('Photo', backref=backref('scrap_photos', cascade='all,delete'))


class PhotoComment(db.Model, BaseMixin):
    """포토-댓글 연결고리"""
    __tablename__ = 'photo_comments'

    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    photo = db.relationship('Photo', back_populates='comments')
    comment = db.relationship('Comment', back_populates='photos')


class Magazine(db.Model, BaseMixin):
    """매거진 정보"""
    __tablename__ = 'magazines'

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    residence_id = db.Column(db.Integer, db.ForeignKey('residences.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.Unicode(255), nullable=False)
    size = db.Column(db.Unicode(255))
    location = db.Column(db.Unicode(255))
    cost = db.Column(db.Unicode(255))
    content = db.Column(db.Text)
    hits = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref=backref('user_magazines'))
    category = db.relationship('Category', backref=backref('category_magazines'))
    residence = db.relationship('Residence', backref=backref('residence_magazines'))
    photos = db.relationship('Photo', back_populates='magazine', cascade='all,delete')
    comments = db.relationship('MagazineComment', back_populates='magazine', cascade='all,delete')

    @hybrid_property
    def vr_count(self):
        return Photo.query.filter(Photo.magazine_id == self.id).filter(Photo.file.has(type=2)).count()

    @hybrid_property
    def mov_count(self):
        return Photo.query.filter(Photo.magazine_id == self.id).filter(Photo.file.has(type=3)).count()

    @hybrid_property
    def has_vr(self):
        return True if self.vr_count else False

    @hybrid_property
    def has_mov(self):
        return True if self.mov_count else False

    @hybrid_method
    def is_active(self, model, user_id):
        return getattr(sys.modules[__name__], model).query.filter_by(magazine_id=self.id, user_id=user_id).first()

    def __repr__(self):
        return "%s(%s)" % (self.title, self.id)


class MagazineLike(db.Model, BaseMixin):
    """스토리-좋아요 연결고리"""
    __tablename__ = 'magazine_likes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    magazine_id = db.Column(db.Integer, db.ForeignKey('magazines.id'))

    user = db.relationship('User', backref=backref('magazine_like_users'))
    magazine = db.relationship('Magazine', backref=backref('like_magazines', cascade='all,delete'))


class MagazineScrap(db.Model, BaseMixin):
    """스토리-좋아요 연결고리"""
    __tablename__ = 'magazine_scraps'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    magazine_id = db.Column(db.Integer, db.ForeignKey('magazines.id'))

    user = db.relationship('User', backref=backref('magazine_scrap_users'))
    magazine = db.relationship('Magazine', backref=backref('scrap_magazines', cascade='all,delete'))


class MagazineComment(db.Model, BaseMixin):
    """매거진-댓글 연결고리"""
    __tablename__ = 'magazine_comments'

    magazine_id = db.Column(db.Integer, db.ForeignKey('magazines.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    magazine = db.relationship('Magazine', back_populates='comments')
    comment = db.relationship('Comment', back_populates='magazines')


class Social(db.Model, BaseMixin):
    __tablename__ = 'socials'

    social_id = db.Column(db.String(64), nullable=False, primary_key=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)


class Professional(db.Model, BaseMixin):
    """전문가 정보"""
    __tablename__ = 'professionals'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    business_no = db.Column(db.Unicode(15), nullable=False)
    phone = db.Column(db.Unicode(15), default="")
    address = db.Column(db.Unicode(255), default="")
    sub_address = db.Column(db.Unicode(255), default="")
    homepage = db.Column(db.Unicode(45), default="")
    greeting = db.Column(db.Text, default="")
    sido_code = db.Column(db.Unicode(2))
    sigungu_code = db.Column(db.Unicode(5))
    post_code = db.Column(db.Integer)
    sido = db.Column(db.Unicode(255), default="")
    sigungu = db.Column(db.Unicode(255), default="")
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'))

    user = db.relationship('User', backref=backref('user_professionals'))

    @hybrid_method
    def get_score(self, professional_id):
        reviews = Review.query.filter(Review.professional_id == professional_id).all()
        sum = 0
        for review in reviews:
            sum += review.score

        if not (len(reviews)).__eq__(0):
            score = sum / (len(reviews))
            score = round(score, 2)
        else:
            score = 0
        return score

    @hybrid_method
    def get_integer(self, score):
        score_integer = int(round(score))
        return score_integer


class BoardCategory(db.Model, BaseMixin):
    """Q&A 카테고리 정보"""
    __tablename__ = 'board_categories'

    name = db.Column(db.Unicode(50), nullable=False)

    def __repr__(self):
        return '[%s]%s' % (self.id, self.name)


class Board(db.Model, BaseMixin):
    """Q&A 게시판"""
    __tablename__ = 'boards'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    board_id = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('board_categories.id'))
    group_id = db.Column(db.Integer)
    depth = db.Column(db.Integer, default=0)
    sort = db.Column(db.Integer, default=0)
    deleted = db.Column(db.Boolean, default=0)
    title = db.Column(db.Unicode(255))
    content = db.Column(db.Text)

    user = db.relationship('User', backref=backref('user_boards'))
    category = db.relationship('BoardCategory', backref=backref('category_boards'))

    @hybrid_property
    def is_reply(self):
        return True if self.depth else False

    @hybrid_property
    def is_deleted(self):
        return self.deleted

    @hybrid_property
    def max1_group_id(self):
        group_id = db.session.query(func.max(Board.group_id)).one()[0]
        return (group_id + 1) if group_id else 1

    @hybrid_property
    def max1_depth(self):
        depth = db.session.query(func.max(Board.depth)).filter_by(board_id=self.board_id, group_id=self.group_id).one()[
            0]
        return (depth + 1) if depth else 1


class Review(db.Model, BaseMixin):
    """댓글 내역"""
    __tablename__ = 'reviews'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'))
    score = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text)

    user = db.relationship('User', backref=backref('user_Reviews'))
    professional = db.relationship('Professional', backref=backref('professional_Reviews'))

    @property
    def project_date(self):
        return self.project_at.strftime('%Y-%m-%d')



class Sclogininteg(db.Model, BaseMixin):
    """로그인정보(통합)"""

    __tablename__ = 'sc_login_integ'
    login_id = db.Column(db.String(100),nullable=False, unique=True)
    login_type = db.Column(db.String(1),nullable=False)
    auth_id = db.Column(db.String(50), db.ForeignKey('sc_auth.id'))
    auth_group = db.Column(db.String(50),nullable=False)


class Scoutterlogininfo(db.Model, BaseMixin):
    """로그인정보(외부)"""

    __tablename__ = 'sc_outter_login_info'
    login_id = db.Column(db.String(100),nullable=False, unique=True)
    login_pwd = db.Column(db.String(128),nullable=False)
    pwd_updated_at = db.Column(db.DateTime,nullable=False,default=db.func.now())
    biz_no = db.Column(db.String(50),db.ForeignKey('sc_comp_info.biz_no'))
    login_yn = db.Column(db.String(2))
    phone = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(75),nullable=False)
    fax_no = db.Column(db.String(30))
    tel_no = db.Column(db.String(75))
    sms_yn = db.Column(db.String(1),nullable=False)
    info_agr_yn = db.Column(db.String(1),nullable=False)
    login_at = db.Column(db.DateTime,default=db.func.now())
    logout_at = db.Column(db.DateTime,default=db.func.now())
    user_ip = db.Column(db.String(20))
    user_host = db.Column(db.String(50))



class Sccompinfo(db.Model, BaseMixin):
    """업체정보"""
    __tablename__ = 'sc_comp_info'
    comp_id = db.Column(db.String(30))
    country_id = db.Column(db.String(30))
    biz_no = db.Column(db.String(50),nullable=False,unique=True)
    vnd_grp_id = db.Column(db.String(30))
    sub_biz_no = db.Column(db.String(30))
    comp_nm = db.Column(db.String(50))
    comp_enm = db.Column(db.String(50))
    addr_1 = db.Column(db.String(50))
    addr_2 = db.Column(db.String(100))
    addr_no = db.Column(db.String(50))
    addr_post = db.Column(db.String(50))
    tel_no = db.Column(db.String(20))
    fax_no = db.Column(db.String(30))
    phone = db.Column(db.String(20))
    vnd_url = db.Column(db.String(100))
    email = db.Column(db.String(75))
    president = db.Column(db.String(50))
    biz_condi = db.Column(db.String(20))
    biz_sector = db.Column(db.String(20))
    pymt_type = db.Column(db.String(30))
    ssn = db.Column(db.String(30))
    language = db.Column(db.String(30))
    part_type = db.Column(db.String(30))
    comp_shrt_nm = db.Column(db.String(30))
    user_ip = db.Column(db.String(50))
    user_host = db.Column(db.String(50))



class Sclogininfo(db.Model, BaseMixin):
    """로그인정보(내부)"""

    __tablename__ = 'sc_login_info'
    login_id = db.Column(db.String(100))
    login_pwd = db.Column(db.String(128),nullable = False)
    pwd_updated_at = db.Column(db.DateTime, nullable = False, default = db.func.now())
    emp_no = db.Column(db.String(20),db.ForeignKey('sc_inner_user_info.emp_no'))
    login_yn = db.Column(db.String(2))
    login_at = db.Column(db.DateTime, nullable = False, default = db.func.now())
    logout_at = db.Column(db.DateTime, nullable = False, default = db.func.now())
    user_ip = db.Column(db.String(20))
    user_host = db.Column(db.String(50))
    login_fail_cnt = db.Column(db.Integer)
    pwd_exp_day = db.Column(db.DateTime, nullable = False, default = db.func.now())




class Scinneruserinfo(db.Model, BaseMixin):
    """내부직원정보"""

    __tablename__ = 'sc_inner_user_info'
    comp_id = db.Column(db.String(20))
    comp_nm = db.Column(db.String(50))
    emp_no = db.Column(db.String(20), nullable = False, unique=True)
    emp_nm = db.Column(db.String(50),db.ForeignKey('sc_inner_user_info.emp_no'))
    emp_enm = db.Column(db.String(50))
    emp_ymd = db.Column(db.DateTime, nullable = False, default = db.func.now())
    ret_ymd = db.Column(db.DateTime, nullable = False, default = db.func.now())
    tel_no = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    fax_no = db.Column(db.String(30))
    mail = db.Column(db.String(75))
    site_id = db.Column(db.String(30))
    site_nm = db.Column(db.String(50))
    division_id = db.Column(db.String(30))
    division_nm = db.Column(db.String(50))
    dept_id = db.Column(db.String(30))
    dept_nm = db.Column(db.String(50))
    cc_id = db.Column(db.String(30))
    cc_nm = db.Column(db.String(100))
    location = db.Column(db.String(40))
    job_rank = db.Column(db.String(30))
    job_spot = db.Column(db.String(30))
    if_stat = db.Column(db.String(1))
    if_log = db.Column(db.String(100))



class Scsystem(db.Model, BaseMixin):
    """공통시스템관리"""
    __tablename__ = 'sc_system'
    sys_id = db.Column(db.String(50),nullable = False, unique=True)
    sys_nm = db.Column(db.String(50), nullable = False, unique=True)




class Scclass(db.Model, BaseMixin):
    """공통클래스관리"""
    __tablename__ = 'sc_class'
    sys_id = db.Column(db.String(50),nullable = False)
    sys_nm = db.Column(db.String(50), nullable = False)
    class_id = db.Column(db.String(30),db.ForeignKey('sc_system.sys_id'), nullable = False, unique=True)
    class_nm = db.Column(db.String(50), db.ForeignKey('sc_system.sys_nm'), nullable = False, unique=True)



class Sccode(db.Model, BaseMixin):
    """공통코드관리"""
    __tablename__ = 'sc_code'
    class_id = db.Column(db.String(30),nullable = False)
    class_nm = db.Column(db.String(50), nullable = False)
    code_id = db.Column(db.String(30),db.ForeignKey('sc_class.class_id'), nullable = False, unique=True)
    code_nm = db.Column(db.String(50), db.ForeignKey('sc_class.class_nm'), nullable = False, unique=True)


class Scmenugroup(db.Model,BaseMixin):
    """공통메뉴그룹관리"""
    __tablename__ = 'sc_menu_group'
    sys_id = db.Column(db.String(50),nullable = False)
    sys_nm = db.Column(db.String(50),nullable = False)
    menugroup_id = db.Column(db.String(30),db.ForeignKey('sc_system.sys_id'),nullable = False,unique=True)
    menugroup_nm = db.Column(db.String(50),db.ForeignKey('sc_system.sys_nm'),nullable = False,unique=True)


class Scmenu(db.Model,BaseMixin):
    """공통메뉴관리"""
    __tablename__ = 'sc_menu'
    menugroup_id = db.Column(db.String(30),db.ForeignKey('sc_menu.menugroup_id'),nullable = False)
    menugroup_nm = db.Column(db.String(50),db.ForeignKey('sc_menu.menugroup_nm'),nullable = False)
    menu_id = db.Column(db.String(50),nullable = False, unique=True)
    menu_nm = db.Column(db.String(50),nullable = False, unique=True)
    depth = db.Column(db.Integer)
    position = db.Column(db.Integer)

class Scgroup(db.Model,BaseMixin):
    """공통그룹관리"""
    __tablename__ = 'sc_group'
    sys_id = db.Column(db.String(50),db.ForeignKey('sc_system.sys_id'),nullable = False)
    sys_nm = db.Column(db.String(50),db.ForeignKey('sc_system.sys_nm'),nullable = False)
    auth_group = db.Column(db.String(20),nullable = False, unique=True)
    group_desc = db.Column(db.String(30),nullable = False, unique=True)

class Scauth(db.Model,BaseMixin):
    """공통권한관리"""
    __tablename__ = 'sc_auth'
    auth_id = db.Column(db.String(50), nullable = False, unique=True)
    auth_nm = db.Column(db.String(50))
    sys_id = db.Column(db.String(50),db.ForeignKey('sc_system.sys_nm'),nullable = False)
    sys_nm = db.Column(db.String(50),db.ForeignKey('sc_system.sys_nm'),nullable = False)
    auth_group = db.Column(db.String(20),db.ForeignKey('sc_group.auth_group'),nullable = False)
    group_desc = db.Column(db.String(30),db.ForeignKey('sc_group.group_desc'),nullable = False)


class Scmenuauth(db.Model,BaseMixin):
    """공통메뉴권한관리"""
    __tablename__ = 'sc_menu_auth'
    auth_id = db.Column(db.String(50),db.ForeignKey('sc_auth.auth_id'),nullable = False)
    menugroup_id = db.Column(db.String(30),db.ForeignKey('sc_menu_group.menugroup_id'),nullable = False)


class Sccodeauth(db.Model,BaseMixin):
    """공통코드권한관리"""
    __tablename__ = 'sc_code_auth'
    auth_id = db.Column(db.String(100),db.ForeignKey('sc_auth.auth_id'),nullable = False)
    class_id = db.Column(db.String(30),db.ForeignKey('sc_class.class_id'),nullable = False)



class Vcapplymaster(db.Model,BaseMixin):
    """출입신청 마스터"""
    __tablename__ = 'vc_apply_master'
    apply_code = db.Column(db.String(50),nullable = False, unique=True)
    apply_nm = db.Column(db.String(50), nullable = False, unique=True)
    interviewr = db.Column(db.String(30), nullable = False)
    applicant = db.Column(db.String(30), nullable = False)
    phone = db.Column(db.String(20), nullable = False)
    visit_category = db.Column(db.String(30), nullable = False)
    biz_no = db.Column(db.String(50), db.ForeignKey('sc_comp_info.biz_no'), nullable = False)
    visit_period = db.Column(db.DateTime)
    visit_purpose = db.Column(db.String(50), nullable = False)
    visit_desc = db.Column(db.String(200), nullable = False)
    site_id = db.Column(db.String(30),db.ForeignKey('sc_code.site_id'), nullable = False)
    site_nm = db.Column(db.String(50),db.ForeignKey('sc_code.site_nm'), nullable = False)
    login_id = db.Column(db.String(100), db.ForeignKey('sc_login_integ.login_no'), nullable = False)


class Vcapplyuser(db.Model,BaseMixin):
    """출입인원 정보"""
    __tablename__ = 'vc_apply_master'
    apply_code = db.Column(db.String(50),db.ForeignKey('vc_apply_master.apply_code'),nullable = False)
    apply_nm = db.Column(db.String(50),db.ForeignKey('vc_apply_master.apply_nm'),nullable = False)
    visitant = db.Column(db.String(30),nullable = False)
    phone = db.Column(db.String(20),nullable = False)
    vehicle_num = db.Column(db.String(10),nullable = False)
    vehicle_type = db.Column(db.String(30),nullable = False)
    vehicle_info = db.Column(db.String(100),nullable = False)
    alien_number = db.Column(db.String(50))
    identify_validation = db.Column(db.String(1),nullable = False)
    personal_information_agreement = db.Column(db.String(1),nullable = False)
    security_agreement = db.Column(db.String(1),nullable = False)
    apply_test = db.Column(db.String(1))
    barcode_code = db.Column(db.String(50),db.ForeignKey('vc_barcode_info.barcode_code'))
    barcode_nm = db.Column(db.String(50),db.ForeignKey('vc_barcode_info.barcode_nm'))


class Vcvehiclemaster(db.Model,BaseMixin):
    """차량출입 마스터"""
    __tablename__ = 'vc_vehicle_master'
    vehicle_code = db.Column(db.String(50),nullable = False,unique="True")
    vehicle_nm = db.Column(db.String(50),nullable = False,unique="True")
    applicant = db.Column(db.String(30),nullable = False)
    phone = db.Column(db.String(20),nullable = False)
    visit_category = db.Column(db.String(30),nullable = False)
    biz_no = db.Column(db.String(50),db.ForeignKey('sc_comp_info.biz_no'),nullable = False)
    visit_period = db.Column(db.DateTime,nullable = False)
    visit_purpose = db.Column(db.String(50))
    visit_desc = db.Column(db.String(200))
    site_id = db.Column(db.String(30),db.ForeignKey('sc_code.site_id'),nullable = False)
    site_nm = db.Column(db.String(50),db.ForeignKey('sc_code.site_nm'),nullable = False)
    login_id = db.Column(db.String(100),db.ForeignKey('sc_login_integ.login_id'),nullable = False)


class Vcvehicleinfo(db.Model,BaseMixin):
    """출입차량 정보"""
    __tablename__ = 'vc_vehicle_info'
    vehicle_code = db.Column(db.String(50),db.ForeignKey('vc_vehicle_master.vehicle_code'),nullable = False)
    vehicle_nm = db.Column(db.String(50), db.ForeignKey('vc_vehicle_master.vehicle_nm'),nullable = False)
    driver = db.Column(db.String(30),nullable = False)
    vehicle_num = db.Column(db.String(10),nullable = False)
    vehicle_type = db.Column(db.String(30),nullable = False)
    vehicle_info = db.Column(db.String(100),nullable = False)
    vehicle_license = db.Column(db.String(100),nullable = False)
    identify_validation = db.Column(db.String(1), nullable=False)
    personal_information_agreement = db.Column(db.String(1), nullable=False)
    security_agreement = db.Column(db.String(1), nullable=False)
    apply_test = db.Column(db.String(1), nullable=False)
    barcode_code = db.Column(db.String(50),db.ForeignKey('vc_barcode_info.barcode_code'), nullable=False)
    barcode_nm = db.Column(db.String(50), db.ForeignKey('vc_barcode_info.barcode_nm'), nullable=False)


class Vcapplyapproval(db.Model,BaseMixin):
    """출입차량 정보"""
    __tablename__ = 'vc_apply_approval'
    approval_code = db.Column(db.String(50),nullable = False, unique= True)
    approval_nm = db.Column(db.String(50),nullable = False, unique= True)
    apply_code = db.Column(db.String(50),db.ForeignKey('vc_apply_master.approval_code'))
    apply_nm = db.Column(db.String(50),db.ForeignKey('vc_apply_master.approval_nm'))
    vehicle_code = db.Column(db.String(50),db.ForeignKey('vc_vehicle_master.vehicle_code'))
    vehicle_nm = db.Column(db.String(50),db.ForeignKey('vc_vehicle_master.vehicle_nm'))
    approval_id = db.Column(db.String(30), nullable=False)
    approval_state = db.Column(db.String(20), nullable=False)
    approval_title = db.Column(db.String(50), nullable=False)
    approval_content = db.Column(db.String(200))
    approval_type = db.Column(db.String(30), nullable=False)


class Vclabelinfo(db.Model,BaseMixin):
    """표찰정보"""
    __tablename__ = 'vc_label_info'
    label_code = db.Column(db.String(50), nullable=False, unqiue=True)
    label_nm = db.Column(db.String(50), nullable=False, unqiue=True)
    approval_code = db.Column(db.String(50), db.ForeignKey('vc_apply_master.approval_code'),nullable=False)
    approval_nm = db.Column(db.String(50,db.ForeignKey('vc_apply_master.approval_nm')),nullable=False)
    label_type = db.Column(db.String(30))
    duedate_start = db.Column(db.DateTime)
    duedate_end = db.Column(db.DateTime)


class Vcbarcodeinfo(db.Model,BaseMixin):
    """바코드정보"""
    __tablename__ = 'vc_barcode_info'
    barcode_code = db.Column(db.String(50),  unqiue=True)
    barcode_nm = db.Column(db.String(50),  unqiue=True)
    label_code = db.Column(db.String(50), db.ForeignKey('vc_label_info.label_code'),nullable=False)
    label_nm = db.Column(db.String(50,db.ForeignKey('vc_label_info.label_nm')),nullable=False)
    barcode_type = db.Column(db.String(45))
    duedate_start = db.Column(db.DateTime)
    duedate_end = db.Column(db.DateTime)



class Vcinoutinfo(db.Model,BaseMixin):
    """입출입정보"""
    __tablename__ = 'vc_barcode_info'
    barcode_code = db.Column(db.String(50),db.ForeignKey('vc_barcode_info.barcode_code'),nullable=False)
    barcode_nm = db.Column(db.String(50),db.ForeignKey('vc_barcode_info.barcode_nm'),nullable=False)
    site_id = db.Column(db.String(30),db.ForeignKey('sc_code.code_id'),nullable=False)
    site_nm = db.Column(db.String(50,db.ForeignKey('sc_code.code_nm'),nullable=False))
    in_area_code = db.Column(db.Integer)
    in_area = db.Column(db.String(100))
    out_area_code = db.Column(db.Column(db.Integer))
    out_area = db.Column(db.String(100))
    in_time = db.Column(db.DateTime)
    out_time = db.Column(db.DateTime)




class Ssctenantdb(db.Model,BaseMixin):
    """테넌트 DB 정보"""
    __tablename__ = 'ssc_tenant_db'
    tenant_id = db.Column(db.String(50),db.ForeignKey('ssc_tenants.tenant_id'),nullable=False)
    host = db.Column(db.String(30))
    port = db.Column(db.String(30))
    user = db.Column(db.String(100))
    password = db.Column(db.String(128))
    schema_nm = db.Column(db.String(50))



class Ssctenantstorage(db.Model,BaseMixin):
    """테넌트 STORAGE 정보"""
    __tablename__ = 'ssc_tenant_storage'
    tenant_id = db.Column(db.String(50),db.ForeignKey('ssc_tenants.tenant_id'))
    bucket_nm = db.Column(db.String(100))
    s3_1 = db.Column(db.String(100))
    s3_2 = db.Column(db.String(100))
    s3_3 = db.Column(db.String(100))
    s3_4 = db.Column(db.String(100))


class Ssctenant(db.Model, BaseMixin):
    """테넌트 정보"""
    __tablename__ = 'ssc_tenants'
    tenant_id = db.Column(db.String(50))
    comp_nm = db.Column(db.String(50))
    comp_id = db.Column(db.String(30))
    country_id = db.Column(db.String(30))
    biz_no = db.Column(db.String(50))
    vnd_grp_id = db.Column(db.String(30))
    sub_biz_no = db.Column(db.String(30))
    comp_enm = db.Column(db.String(50))
    addr_1 = db.Column(db.String(30))
    addr_2 = db.Column(db.String(100))
    addr_no = db.Column(db.String(50))
    addr_post = db.Column(db.String(50))
    tel_no = db.Column(db.String(20))
    fax_no = db.Column(db.String(30))
    phone = db.Column(db.String(20))
    vnd_url = db.Column(db.String(100))
    vnd_email = db.Column(db.String(75))
    president = db.Column(db.String(50))
    biz_condi = db.Column(db.String(20))
    biz_sector = db.Column(db.String(20))
    pymt_type = db.Column(db.String(30))
    ssn = db.Column(db.String(30))
    language = db.Column(db.String(30))
    part_type = db.Column(db.String(30))
    comp_shrt_nm = db.Column(db.String(30))
    tenant_group_id = db.Column(db.String(30))
    tenant_group_nm = db.Column(db.String(50))
    event_url = db.Column(db.String(100))
    background_img = db.Column(db.String(100))
    logo_img = db.Column(db.String(100))
