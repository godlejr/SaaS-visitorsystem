import sys

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from flask_login import UserMixin
from sqlalchemy.orm import backref, relationship

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
    use_yn = db.Column(db.String(1), default='1')
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


# ===============================================================================================================================================
# 방문객 관리 VMS
# ===============================================================================================================================================

# ===============================================================================================================================================
# 001.시스템 공통
# ===============================================================================================================================================

class Ssctenant(db.Model, BaseMixin):
    """테넌트 정보"""
    __tablename__ = 'ssc_tenants'
    tenant_id = db.Column(db.String(50))  # 테넌트 String정보
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

    # 1:多 (Ssctenant->Ssctenantdb)
    sctenantdbs = db.relationship('Ssctenantdb', back_populates='ssctenant')

    # 1:多 (Ssctenantdb->Ssctenantstorage)
    ssctenantstorages = db.relationship('Ssctenantstorage', back_populates='ssctenant')

    # 1:多 (Ssctenant->Scuser) [Master]
    scusers = db.relationship('Scuser', back_populates='ssctenant')


class Ssctenantdb(db.Model, BaseMixin):
    """테넌트 DB 정보"""
    __tablename__ = 'ssc_tenant_db'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    host = db.Column(db.String(30))
    port = db.Column(db.String(30))
    user = db.Column(db.String(100))
    password = db.Column(db.String(128))
    schema_nm = db.Column(db.String(50))

    #Detail
    ssctenant = db.relationship('Ssctenant', backref=backref('FK_SSC_TENANT_DB_TENANT_ID'))


class Ssctenantstorage(db.Model, BaseMixin):
    """테넌트 STORAGE 정보"""
    __tablename__ = 'ssc_tenant_storage'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'))
    bucket_nm = db.Column(db.String(100))
    s3_1 = db.Column(db.String(100))
    s3_2 = db.Column(db.String(100))
    s3_3 = db.Column(db.String(100))
    s3_4 = db.Column(db.String(100))
    # Detail - 자식
    ssctenant = db.relationship('Ssctenant', backref=backref('FK_SSC_TENANT_storage_TENANT_ID'))


# ===============================================================================================================================================
# 002.내방객 공통
# ===============================================================================================================================================

class Scclass(db.Model, BaseMixin):
    """공통클래스관리"""
    __tablename__ = 'sc_class'
    class_cd = db.Column(db.String(30), nullable=False, unique=True)
    class_nm = db.Column(db.String(50))
    user_def_yn = db.Column(db.String(1))

    # 1:多 (Scclass->Sccode)-Parent class 정의 - childs = db.relationship('Child ', back_populates='Child 클래스에 정의한 parent 변수명')
    sccodes = db.relationship('Sccode', back_populates='scclass')

class Sccode(db.Model, BaseMixin):
    """공통코드관리"""
    __tablename__ = 'sc_code'
    tenant_id = db.Column(db.Integer, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('sc_class.id'), nullable=False)
    class_nm = db.Column(db.String(50))
    code = db.Column(db.String(30), nullable=False)
    code_nm = db.Column(db.String(50))
    attb_a = db.Column(db.String(50))
    attb_b = db.Column(db.String(50))
    depth = db.Column(db.Integer)
    group_id = db.Column(db.String(50))
    position = db.Column(db.Integer)


    # [Detail] -Child class 정의 - parent = db.relationship('Parent', backref=backref('실제 DB FK명'))
    scclass = db.relationship('Scclass', backref=backref('FK_SC_CODE_CLASS_ID'))


    @hybrid_property
    def get_site_for_gate(self):
        return db.session.query(Sccode).filter(Sccode.tenant_id == self.tenant_id, Sccode.use_yn == '1',
                                               Sccode.class_nm == '사업장', Sccode.code == self.attb_a).first()



# 권한 매핑 필요
class Sccodeauth(db.Model, BaseMixin):
    """공통코드권한관리"""
    __tablename__ = 'sc_code_auth'
    auth_id = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.String(30), db.ForeignKey('sc_class.class_id'), nullable=False)

class Sccompinfo(db.Model, BaseMixin):
    """업체정보"""
    __tablename__ = 'sc_comp_info'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    comp_id = db.Column(db.String(30))
    country_id = db.Column(db.String(30))
    biz_no = db.Column(db.String(50), nullable=False, unique=True)
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

    # 1:多 (Sccompinfo->Scuser) [Master]
    scusers = db.relationship('Scuser', back_populates='sccompinfo')

    # 1:多 (Sccompinfo->Scuser) [Master]
    vcapplymasters = db.relationship('Vcapplymaster', back_populates='sccompinfo')


class Scinneruserinfo(db.Model, BaseMixin):
    """내부직원정보"""

    __tablename__ = 'sc_inner_user_info'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    comp_id = db.Column(db.String(20))
    comp_nm = db.Column(db.String(50))
    emp_no = db.Column(db.String(20), nullable=False, unique=True)
    emp_nm = db.Column(db.String(50))
    emp_enm = db.Column(db.String(50))
    emp_ymd = db.Column(db.DateTime)
    ret_ymd = db.Column(db.DateTime)
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

    # 1:多 (Scinneruserinfo->Scuser) [Master]
    scusers = db.relationship('Scuser', back_populates='scinneruserinfo')


class Scmenu(db.Model, BaseMixin):
    """공통메뉴관리"""
    __tablename__ = 'sc_menu'
    menu_cd = db.Column(db.String(50), nullable=False, unique=True)
    menu_nm = db.Column(db.String(50))
    depth = db.Column(db.Integer)
    position = db.Column(db.Integer)
    group_id = db.Column(db.String(50))
    group_nm = db.Column(db.String(200))
    url = db.Column(db.String(200))

    # 1:多 (Scmenu->Scmenuauth) [Master]
    scmenuauths = db.relationship('Scmenuauth', back_populates='scmenu')


class Scmenuauth(db.Model, BaseMixin):
    """공통메뉴권한관리"""
    __tablename__ = 'sc_menu_auth'
    auth_id = db.Column(db.String(50), nullable=False)
    menu_id = db.Column(db.String(30), db.ForeignKey('sc_menu.id'), nullable=False)

    # [Detail]
    scmenu = db.relationship('Scmenu', backref=backref('FK_sc_menu_auth_menu_ID'))


class Scuser(db.Model, UserMixin):
    """사용자 정보"""
    __tablename__ = 'sc_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    use_yn = db.Column(db.String(1))
    created_at = db.Column(db.DateTime, default=db.func.now())
    created_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    updated_by = db.Column(db.String(50))
    end_at = db.Column(db.DateTime, default=db.func.now())

    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    login_id = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(256), nullable=False)
    login_pwd = db.Column(db.String(256), nullable=False)
    pwd_updated_at = db.Column(db.DateTime)
    login_fail_cnt = db.Column(db.Integer)
    user_type = db.Column(db.String(1), nullable=False)  # 내부0 외부1
    auth_id = db.Column(db.String(50))
    emp_id = db.Column(db.Integer,db.ForeignKey('sc_inner_user_info.id'))
    biz_id = db.Column(db.Integer,db.ForeignKey('sc_comp_info.id'))  # 외부1일 경우에만 데이터 있음 sc_comp_info
    comp_nm = db.Column(db.String(50))
    login_yn = db.Column(db.String(2))
    # dept_id/dept_nm 추가
    dept_id = db.Column(db.String(30))
    dept_nm = db.Column(db.String(50))
    site_nm = db.Column(db.String(50))
    phone = db.Column(db.String(512))
    email = db.Column(db.String(512))
    fax_no = db.Column(db.String(512))
    tel_no = db.Column(db.String(512))
    sms_yn = db.Column(db.String(1))
    info_agr_yn = db.Column(db.String(1))
    login_at = db.Column(db.DateTime)
    logout_at = db.Column(db.DateTime)
    user_ip = db.Column(db.String(20))
    user_host = db.Column(db.String(50))
    site_nm = db.Column(db.String(512))

    # [Detail] : Child class 정의 - parent = db.relationship('Parent', backref=backref('실제 DB FK명'))
    ssctenant = db.relationship('Ssctenant', backref=backref('FK_SC_USER_TENANT_ID'))

    # [Detail]
    scinneruserinfo = db.relationship('Scinneruserinfo', backref=backref('FK_SC_USER_EMP_ID'))

    # [Detail]
    sccompinfo = db.relationship('Sccompinfo', backref=backref('FK_SC_USER_BIZ_ID'))

    # 1:多 Parent class 정의 - childs = db.relationship('Child ', back_populates='Child 클래스에 정의한 parent 변수명')
    vcapplymasters = db.relationship('Vcapplymaster', back_populates='scuser')

    @hybrid_property
    def created_date(self):
        return self.created_at.strftime('%Y-%m-%d')

    @hybrid_property
    def updated_date(self):
        return self.updated_at.strftime('%Y-%m-%d')

    @hybrid_method
    def get_id(self):
        return self.login_id


    @hybrid_property
    def get_auth(self):
        #권한은 테넌트 조건이 없음..
        return db.session.query(Sccode).filter(Sccode.use_yn == '1', Sccode.class_nm == '권한', Sccode.code == self.auth_id).first()


class Vcapplymaster(db.Model, BaseMixin):
    """방문신청 마스터"""
    __tablename__ = 'vc_apply_master'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    interviewr = db.Column(db.String(30), nullable=False)
    applicant = db.Column(db.String(30), nullable=False)
    applicant_comp_id = db.Column(db.String(30))
    applicant_comp_nm = db.Column(db.String(50))
    phone = db.Column(db.String(20), nullable=False)
    visit_category = db.Column(db.String(30), nullable=False)
    biz_id = db.Column(db.Integer, db.ForeignKey('sc_comp_info.id'), nullable=False)
    visit_sdate = db.Column(db.String(50), nullable=False)
    visit_edate = db.Column(db.String(50), nullable=False)
    visit_purpose = db.Column(db.String(50), nullable=False)
    visit_desc = db.Column(db.String(200))
    site_id = db.Column(db.String(30), nullable=False)
    site_nm = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('sc_user.id'), nullable=False) #신청자 아이디
    interview_id = db.Column(db.Integer, nullable=False)  # 접견관 아이디
    approval_state = db.Column(db.String(20), nullable=False)
    # 추가부분
    site_id2 = db.Column(db.String(30), nullable=False)
    site_nm2 = db.Column(db.String(50), nullable=False)
    visit_type = db.Column(db.String(50)) #0(로그인 한 사용자, 작업자용) #1(로그인 안 함 사용자, 일반사용자용)
    #승인일시 컬럼 추가
    approval_date = db.Column(db.String(50), nullable=False)

    # [Detail] Child class 정의 - parent = db.relationship('Parent', backref=backref('실제 DB FK명'))
    sccompinfo = db.relationship('Sccompinfo', backref=backref('FK_VC_APPLY_MASTER_BIZ_ID'))

    # [Detail]
    scuser = db.relationship('Scuser', backref=backref('FK_VC_APPLY_MASTER_LOGIN_ID'))

    # 1:多 (Vcapplymaster->Vcapplyuser) [Master]
    vcapplyusers = db.relationship('Vcapplyuser', back_populates='vcapplymaster')

    # 1:多 (Vcapplymaster->Vcvisituser) [Master] 신규
    Vcvisitusers = db.relationship('Vcvisituser', back_populates='vcapplymaster')


    @hybrid_property
    def get_interviewer(self):
        #권한은 테넌트 조건이 없음..
        return db.session.query(Scuser).filter(Scuser.tenant_id == self.tenant_id ,Scuser.use_yn == '1', Scuser.id == self.interview_id).first()

class Vcapplyuser(db.Model, BaseMixin):
    """방문인원 정보"""
    __tablename__ = 'vc_apply_user'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    apply_id = db.Column(db.Integer, db.ForeignKey('vc_apply_master.id'), nullable=False)

    visitant = db.Column(db.String(30))
    phone = db.Column(db.String(20))
    vehicle_num = db.Column(db.String(10))
    vehicle_type = db.Column(db.String(30))
    barcode = db.Column(db.String(50))
    barcode_type = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))

    # [Detail]
    vcapplymaster = db.relationship('Vcapplymaster', backref=backref('FK_VC_APPLY_USER_APPLY_ID'))

    # 1:多 (Vcapplyuser->Vcinoutinfo) [Master]
    vcinoutinfos = db.relationship('Vcinoutinfo', back_populates='vcapplyuser')


class Vcinoutinfo(db.Model, BaseMixin):
    """입방문정보"""
    __tablename__ = 'vc_inout_info'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    apply_user_id = db.Column(db.Integer, db.ForeignKey('vc_apply_user.id'), nullable=False)

    site_id = db.Column(db.String(30))
    site_nm = db.Column(db.String(50))
    in_area_cd = db.Column(db.String(30))
    in_area_nm = db.Column(db.String(50))
    out_area_cd = db.Column(db.String(30))
    out_area_nm = db.Column(db.String(50))
    in_time = db.Column(db.String(50))
    out_time = db.Column(db.String(50))

    # [Detail]
    vcapplyuser = db.relationship('Vcapplyuser', backref=backref('FK_VC_INOUT_INFO_APPLY_USER_ID'))


class Scrule(db.Model, BaseMixin):
    """테넌트 정보"""
    __tablename__ = 'sc_rule'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    rule_name = db.Column(db.String(50), nullable=False, unique=True)
    rule_type = db.Column(db.String(50), nullable=False)
    rule_duedate = db.Column(db.String(50), nullable=False)
    rule_desc = db.Column(db.String(100), nullable=False)
    rule_tlocation = db.Column(db.String(50), nullable=False, default='test')

    # 1:多 (Scrule->Vcvisituser) [Master]
    vcvisitusers = db.relationship('Vcvisituser', back_populates='scrule')

    # 1:多 (Scrule->ScRuleFile) [Master]
    scrulefiles = db.relationship('ScRuleFile', back_populates='scrule')


class Vcvisituser(db.Model, BaseMixin):
    """작업자 정보"""
    __tablename__ = 'vc_visit_user'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey('sc_rule.id'), nullable=False)
    apply_id = db.Column(db.Integer, db.ForeignKey('vc_apply_master.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    text_desc = db.Column(db.String(100))
    s_date = db.Column(db.String(50))
    e_date = db.Column(db.String(50))

    # [Detail]
    scrule = db.relationship('Scrule', backref=backref('VC_VISIT_USER_RULE_ID'))
    vcapplymaster = db.relationship('Vcapplymaster', backref=backref('VC_VISIT_USER_APPLY_ID'))

    # 1:多 (Vcvisituser->ScRuleFile) [Master]
    scrulefiles = db.relationship('ScRuleFile', back_populates='vcvisituser')


class Vcstackuser(db.Model, BaseMixin):
    """작업자 스택 정보"""
    __tablename__ = 'vc_stack_user'
    tenant_id = db.Column(db.Integer, nullable=False)
    rule_id = db.Column(db.Integer,db.ForeignKey('sc_rule.id'), nullable=False)
    apply_id = db.Column(db.Integer)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    text_desc = db.Column(db.String(100))
    s_date = db.Column(db.String(50))
    e_date = db.Column(db.String(50))

    # [Detail]
    scrule = db.relationship('Scrule', backref=backref('VC_STACK_USER_RULE_ID'))

    # 1:多 (Vcstackuser->ScRuleFile) [Master]
    scrulefiles = db.relationship('ScRuleFile', back_populates='vcstackuser')


class ScRuleFile(db.Model, BaseMixin):
    """파일 정보"""
    __tablename__ = 'sc_rule_file'
    tenant_id = db.Column(db.Integer, db.ForeignKey('ssc_tenants.id'), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey('sc_rule.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('vc_visit_user.id'), nullable=False)
    visit_stack_id = db.Column(db.Integer, db.ForeignKey('vc_stack_user.id'))
    file_dir = db.Column(db.String(100))
    file_name = db.Column(db.String(100))
    s3_url = db.Column(db.String(200))


    # [Detail]
    scrule = db.relationship('Scrule', backref=backref('sc_rule_file_sc_rule'))
    vcvisituser = db.relationship('Vcvisituser', backref=backref('sc_rule_file_vc_visit_user'))
    vcstackuser = db.relationship('Vcstackuser', backref=backref('sc_rule_file_vc_stack_user'))
