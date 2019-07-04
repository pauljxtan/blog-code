import peewee as pw
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

cache = CacheManager(**parse_cache_config_options({'cache.type': 'memory'}))

db = pw.SqliteDatabase('tagger.db')

# -- Models

class BaseModel(pw.Model):
    class Meta:
        database = db

class File(BaseModel):
    name = pw.CharField(unique=True)

class Tag(BaseModel):
    name = pw.CharField(unique=True)

class FileTag(BaseModel):
    tag = pw.ForeignKeyField(Tag)
    fil = pw.ForeignKeyField(File)

# -- Queries

def create_filetag(filename, tagname):
    cache.invalidate(get_file_tags, 'get_file_tags_cache', filename)
    cache.invalidate(get_num_files_with_tag, 'get_num_files_with_tag_cache', tagname)

    fil, _created = File.get_or_create(name=filename)
    tag, tag_created = Tag.get_or_create(name=tagname)
    _, filetag_created = FileTag.get_or_create(fil=fil, tag=tag)
    return filetag_created

@cache.cache('get_file_tags_cache')
def get_file_tags(filename):
    tags = (Tag.select(Tag.name).join(FileTag).join(File).where(File.name == filename).order_by(
        Tag.name.asc()))
    # Separate DB hit per tag here isn't ideal, but the caching helps
    return [(tag.name, get_num_files_with_tag(tag.name)) for tag in tags]

@cache.cache('get_num_files_with_tag_cache')
def get_num_files_with_tag(tagname):
    tag = Tag.get_or_none(name=tagname)
    return FileTag.select().where(FileTag.tag == tag).count() if tag else 0

def delete_filetag(filename, tagname):
    cache.invalidate(get_file_tags, 'get_file_tags_cache', filename)
    cache.invalidate(get_num_files_with_tag, 'get_num_files_with_tag_cache', tagname)

    fil = File.get_or_none(name=filename)
    tag = Tag.get_or_none(name=tagname)
    # Return number of rows modified
    return FileTag.delete().where((FileTag.fil == fil) & (FileTag.tag == tag)).execute()
