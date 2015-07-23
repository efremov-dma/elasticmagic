from __future__ import absolute_import
from collections import defaultdict

from . import actions
from .util import to_camel_case
from .search import SearchQuery
from .result import Result
from .document import DynamicDocument
from .expression import Params


class Index(object):
    def __init__(self, cluster, name):
        self._cluster = cluster
        self._name = name

        self._doc_cls_cache = {}

    def __getattr__(self, name):
        return self.get_doc_cls(name)

    def get_doc_cls(self, name):
        if name not in self._doc_cls_cache:
            self._doc_cls_cache[name] = type(
                '{}{}'.format(to_camel_case(name), 'Document'),
                (DynamicDocument,),
                {'__doc_type__': name}
            )
        return self._doc_cls_cache[name]

    def search_query(self, *args, **kwargs):
        kwargs['index'] = self
        return SearchQuery(*args, **kwargs)

    query = search_query

    # Methods that do requests to elasticsearch

    def get(self, id, doc_cls=None, doc_type=None, source=None,
            realtime=None, routing=None, preference=None, refresh=None,
            version=None, version_type=None):
        return self._cluster.get(
            self._name, id, doc_cls=doc_cls, doc_type=doc_type, source=source,
            realtime=realtime, routing=routing, preference=preference, refresh=refresh,
            version=version, version_type=version_type
        )

    def multi_get(self, docs, doc_type=None, source=None,
            realtime=None, routing=None, preference=None, refresh=None):
        return self._cluster.multi_get(
            docs, index=self._name, doc_type=doc_type, source=source,
            realtime=realtime, routing=routing, preference=preference, refresh=refresh,
        )

    mget = multi_get

    def search(self, q, doc_type=None, routing=None, preference=None, search_type=None, scroll=None):
        return self._cluster.search(
            q, index=self._name, doc_type=doc_type, 
            routing=routing, preference=preference, search_type=search_type, scroll=scroll,
        )

    def multi_search(self, queries, doc_type=None, routing=None, preference=None, search_type=None):
        return self._cluster.multi_search(
            queries, index=self._name, doc_type=doc_type,
            routing=routing, preference=preference, search_type=search_type,
        )

    msearch = multi_search

    def count(self, q, doc_type=None, routing=None, preference=None):
        return self._cluster.count(
            q, index=self._name, doc_type=doc_type, routing=routing, preference=preference,
        )

    def exists(self, q, doc_type=None, refresh=None, routing=None):
        return self._cluster.exists(
            q, index=self._name, doc_type=doc_type, refresh=refresh, routing=routing,
        )

    def scroll(self, scroll_id, scroll, doc_cls=None, instance_mapper=None):
        return self._cluster.scroll(
            scroll_id, scroll, doc_cls=doc_cls, instance_mapper=instance_mapper,
        )

    def put_mapping(self, doc_cls_or_mapping, doc_type=None, allow_no_indices=None,
                    expand_wildcards=None, ignore_conflicts=None, ignore_unavailable=None,
                    master_timeout=None, timeout=None):
        return self._cluster.put_mapping(
            doc_cls_or_mapping, index=self._name, doc_type=doc_type,
            allow_no_indices=allow_no_indices, expand_wildcards=expand_wildcards,
            ignore_conflicts=ignore_conflicts, ignore_unavailable=ignore_unavailable,
            master_timeout=master_timeout, timeout=timeout
        )

    def add(self, docs, doc_type=None, timeout=None, consistency=None, replication=None):
        acts = []
        for doc in docs:
            acts.append(actions.Index(doc))
        self._cluster.bulk(
            acts, index=self._name, doc_type=doc_type,
            timeout=timeout, consistency=consistency, replication=replication
        )

    def delete(self, doc, doc_type=None, timeout=None, consistency=None, replication=None,
               parent=None, routing=None, refresh=None, version=None, version_type=None):
        return self._cluster.delete(
            doc, index=self._name, doc_type=doc_type, 
            timeout=timeout, consistency=consistency, replication=replication,
            parent=parent, routing=routing, refresh=refresh,
            version=version, version_type=version_type,
        )

    def delete_by_query(self, q, doc_type=None, timeout=None, consistency=None, replication=None, routing=None):
        return self._cluster.delete_by_query(
            q, index=self._name, doc_type=doc_type,
            timeout=timeout, consistency=consistency, replication=replication, routing=routing
        )

    def bulk(self, actions, doc_type=None, refresh=None):
        return self._cluster.bulk(
            actions, index=self._name, doc_type=doc_type, refresh=refresh,
        )
        
    def refresh(self):
        return self._cluster.refresh(index=self._name)
        
    def flush(self):
        return self._cluster.flush(index=self._name)
