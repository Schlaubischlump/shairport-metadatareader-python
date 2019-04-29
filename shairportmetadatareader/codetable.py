# -*- coding: utf-8 -*-
"""
Core and shairport-sync codes send by shairport-sync.
"""
CORE = "core"
SSNC = "ssnc"

# code: dmap.readable_code, data_type
# the datatypes for some of these objects might be wrong
# https://github.com/jkiddo/jolivia/blob/46e53969d4b4bfb4a538511591b9ad2a8f3fca80/jolivia.protocol/src/main/java/org/dyndns/jkiddo/dmp/IDmapProtocolDefinition.java#L154
CORE_CODE_DICT = {
    "asaa": ("songalbumartist", "str"),                 # daap.songalbumartist
    "agal": ("unknown_al", "str"),                      # com.apple.itunes.unknown-al
    "agar": ("ar", "str"),                              # "unknown.ar
    "apro": ("protocolversion", "str"),                 # daap.protocolversion
    "abpl": ("baseplaylist", "int"),                    # daap.baseplaylist
    "abal": ("browsealbumlisting", "str"),              # daap.browsealbumlisting
    "abar": ("browseartistlisting", "str"),             # daap.browseartistlisting
    "abcp": ("browsecomposerlisting", "str"),           # daap.browsecomposerlisting
    "abgn": ("browsegenrelisting", "str"),              # daap.browsegenrelisting
    "abro": ("databasebrowse", "str"),                  # daap.databasebrowse
    "aply": ("databaseplaylists", "str"),               # daap.databaseplaylists
    "adbs": ("databasesongs", "str"),                   # daap.databasesongs
    "aeCs": ("artworkchecksum", "int"),                 # com.apple.itunes.artworkchecksum
    "aeCF": ("cloud_flavor_id", "int"),                 # com.apple.itunes.cloud-flavor-id
    "aeCd": ("cloud_id", "int"),                        # com.apple.itunes.cloud-id
    "aeCK": ("cloud_library_kind", "int"),              # com.apple.itunes.cloud-library-kind
    "aeCM": ("cloud_status", "int"),                    # com.apple.itunes.cloud-status
    "aeCU": ("cloud_user_id", "int"),                   # com.apple.itunes.cloud-user-id
    "aecp": ("collection_description", "str"),          # com.apple.itunes.collection-description
    "aeCR": ("content_rating", "str"),                  # com.apple.itunes.content-rating
    "aeK1": ("drm_key1_id", "int"),                     # com.apple.itunes.drm-key1-id
    "aeK2": ("drm_key2_id", "int"),                     # com.apple.itunes.drm-key2-id
    "aeDP": ("drm_platform_id", "int"),                 # com.apple.itunes.drm-platform-id
    "aeDR": ("drm_user_id", "int"),                     # com.apple.itunes.drm-user-id
    "aeDV": ("drm_versions", "int"),                    # com.apple.itunes.drm-versions
    "aeEN": ("episode_num_str", "str"),                 # com.apple.itunes.episode-num-str
    "aeES": ("episode_sort", "int"),                    # com.apple.itunes.episode-sort
    "aeMk": ("extended_media_kind", "int"),             # com.apple.itunes.extended-media-kind
    "aeGU": ("gapless_dur", "int"),                     # com.apple.itunes.gapless-dur
    "aeGE": ("gapless_enc_del", "int"),                 # com.apple.itunes.gapless-enc-del
    "aeGD": ("gapless_enc_dr", "int"),                  # com.apple.itunes.gapless-enc-dr
    "aeGH": ("gapless_heur", "int"),                    # com.apple.itunes.gapless-heur
    "aeGR": ("gapless_resy", "int"),                    # com.apple.itunes.gapless-resy
    "aeGs": ("can_be_genius_seed", "bool"),             # com.apple.itunes.can-be-genius-seed
    "aeHV": ("has_video", "bool"),                      # com.apple.itunes.has-video
    "aeHD": ("is_hd_video", "bool"),                    # com.apple.itunes.is-hd-video
    "aeAI": ("itms_artistid", "int"),                   # com.apple.itunes.itms-artistid
    "aeCI": ("itms_composerid", "int"),                 # com.apple.itunes.itms-composerid
    "aeGI": ("itms_genreid", "int"),                    # com.apple.itunes.itms-genreid
    "aePI": ("itms_playlistid", "int"),                 # com.apple.itunes.itms-playlistid
    "aeSI": ("itms_songid", "int"),                     # com.apple.itunes.itms-songid
    "aeSF": ("itms_storefrontid", "int"),               # com.apple.itunes.itms-storefrontid
    "aels": ("liked_state", "int"),                     # com.apple.itunes.liked-state
    "aeMK": ("mediakind", "int"),                       # com.apple.itunes.mediakind
    "aeml": ("media_kind_listing", "str"),              # com.apple.itunes.media-kind-listing
    "aemi": ("media_kind_listing_item", "str"),         # com.apple.itunes.media-kind-listing-item
    "aeMX": ("movie_info_xml", "str"),                  # com.apple.itunes.movie-info-xml
    "aeSV": ("music_sharing_version", "int"),           # com.apple.itunes.music-sharing-version
    "aeNN": ("network_name", "str"),                    # com.apple.itunes.network-name
    "aeND": ("non_drm_user_id", "int"),                 # com.apple.itunes.non-drm-user-id
    "aeNV": ("norm_volume", "int"),                     # com.apple.itunes.norm-volume
    "aePC": ("is_podcast", "bool"),                     # com.apple.itunes.is-podcast
    "aePP": ("is_podcast_playlist", "bool"),            # com.apple.itunes.is-podcast-playlist
    "aeSG": ("saved_genius", "bool"),                   # com.apple.itunes.saved-genius
    "aeSU": ("season_num", "int"),                      # com.apple.itunes.season-num
    "aeSN": ("series_name", "str"),                     # com.apple.itunes.series-name
    "aeSP": ("smart_playlist", "int"),                  # com.apple.itunes.smart-playlist
    "asrs": ("songuserratingstatus", "int"),            # daap.songuserratingstatus
    "aePS": ("special_playlist", "bool"),               # com.apple.itunes.special-playlist
    "aeSE": ("store_pers_id", "int"),                   # com.apple.itunes.store-pers-id
    "aeFP": ("unknown_FP", "int"),                      # com.apple.itunes.unknown-FP
    "aeAK": ("unknown", "str"),                         # unknown
    "aeCS": ("artworkchecksum", "int"),                 # com.apple.itunes.artworkchecksum
    "aeFR": ("unknown_FR", "int"),                      # com.apple.itunes.unknown-FR
    "aeIM": ("unknown_IM", "int"),                      # com.apple.itunes.unknown-IM
    "aeMQ": ("unknown_MQ", "int"),                      # com.apple.itunes.unknown-MQ
    "aeRM": ("unknown_RM", "int"),                      # com.apple.itunes.unknown-RM
    "aeSL": ("unknown_SL", "int"),                      # com.apple.itunes.unknown-SL
    "aeSR": ("unknown_SR", "int"),                      # com.apple.itunes.unknown-SR
    "aeSX": ("unknown_SX", "int"),                      # com.apple.itunes.unknown-SX
    "aeTr": ("unknown_Tr", "int"),                      # com.apple.itunes.unknown-Tr
    "aeXD": ("xid", "str"),                             # com.apple.itunes.xid
    "agac": ("groupalbumcount", "int"),                 # daap.groupalbumcount
    "apso": ("playlistsongs", "str"),                   # daap.playlistsongs
    "aprm": ("playlistrepeatmode", "int"),              # daap.playlistrepeatmode
    "apsm": ("playlistshufflemode", "int"),             # daap.playlistshufflemode
    "arsv": ("resolve", "str"),                         # daap.resolve
    "arif": ("resolveinfo", "str"),                     # daap.resolveinfo
    "avdb": ("serverdatabases", "str"),                 # daap.serverdatabases
    "asal": ("songalbum", "str"),                       # daap.songalbum
    "asai": ("songalbumid", "int"),                     # daap.songalbumid
    "aslr": ("songalbumuserrating", "int"),             # daap.songalbumuserrating
    "asas": ("songalbumuserratingstatus", "int"),       # daap.songalbumuserratingstatus
    "asar": ("songartist", "str"),                      # daap.songartist
    "asri": ("songartistid", "int"),                    # daap.songartistid
    "asac": ("songartworkcount", "int"),                # daap.songartworkcount
    "asbt": ("songbeatsperminute", "int"),              # daap.songbeatsperminute
    "asbr": ("songbitrate", "int"),                     # daap.songbitrate
    "asct": ("songcategory", "str"),                    # daap.songcategory
    "ascs": ("songcodecsubtype", "int"),                # daap.songcodecsubtype
    "ascd": ("songcodectype", "str"),                   # daap.songcodectype
    "ascm": ("songcomment", "str"),                     # daap.songcomment
    "asco": ("songcompilation", "bool"),                # daap.songcompilation
    "ascp": ("songcomposer", "str"),                    # daap.songcomposer
    "ascn": ("songcontentdescription", "str"),          # daap.songcontentdescription
    "ascr": ("songcontentrating", "int"),               # daap.songcontentrating
    "asdk": ("songdatakind", "int"),                    # daap.songdatakind
    "asul": ("songdataurl", "str"),                     # daap.songdataurl
    "asda": ("songdateadded", "date"),                  # daap.songdateadded
    "asdm": ("songdatemodified", "date"),               # daap.songdatemodified
    "aspl": ("songdateplayed", "date"),                 # daap.songdateplayed
    "asdp": ("songdatepurchased", "date"),              # daap.songdatepurchased
    "asdr": ("songdatereleased", "date"),               # daap.songdatereleased
    "asdt": ("songdescription", "str"),                 # daap.songdescription
    "asdb": ("songdisabled", "bool"),                   # daap.songdisabled
    "asdc": ("songdisccount", "int"),                   # daap.songdisccount
    "asdn": ("songdiscnumber", "int"),                  # daap.songdiscnumber
    "aseq": ("songeqpreset", "str"),                    # daap.songeqpreset
    "ases": ("songexcludefromshuffle", "bool"),         # daap.songexcludefromshuffle
    "ased": ("songextradata", "int"),                   # daap.songextradata
    "asfm": ("songformat", "str"),                      # daap.songformat
    "asgp": ("songgapless", "bool"),                    # daap.songgapless
    "asgn": ("songgenre", "str"),                       # daap.songgenre
    "agrp": ("songgrouping", "str"),                    # daap.songgrouping
    "ashp": ("songhasbeenplayed", "bool"),              # daap.songhasbeenplayed
    "asky": ("songkeywords", "str"),                    # daap.songkeywords
    "askd": ("songlastskipdate", "date"),               # daap.songlastskipdate
    "aslc": ("songlongcontentdescription", "str"),      # daap.songlongcontentdescription
    "asls": ("songlongsize", "int"),                    # daap.songlongsize
    "aspu": ("songpodcasturl", "str"),                  # daap.songpodcasturl
    "asrv": ("songrelativevolume", "int"),              # daap.songrelativevolume
    "assr": ("songsamplerate", "int"),                  # daap.songsamplerate
    "assz": ("songsize", "int"),                        # daap.songsize
    "asst": ("songstarttime", "int"),                   # daap.songstarttime
    "assp": ("songstoptime", "int"),                    # daap.songstoptime
    "astm": ("songtime", "int"),                        # daap.songtime
    "astc": ("songtrackcount", "int"),                  # daap.songtrackcount
    "astn": ("songtracknumber", "int"),                 # daap.songtracknumber
    "aspc": ("songuserplaycount", "int"),               # daap.songuserplaycount
    "asur": ("songuserrating", "int"),                  # daap.songuserrating
    "askp": ("songuserskipcount", "int"),               # daap.songuserskipcount
    "asyr": ("songyear", "int"),                        # daap.songyear
    "assu": ("sortalbum", "str"),                       # daap.sortalbum
    "assl": ("sortalbumartist", "str"),                 # daap.sortalbumartist
    "assa": ("sortartist", "str"),                      # daap.sortartist
    "asbk": ("bookmarkable", "bool"),                   # daap.bookmarkable
    "assc": ("sortcomposer", "str"),                    # daap.sortcomposer
    "assn": ("sortname", "str"),                        # daap.sortname
    "asss": ("sortseriesname", "str"),                  # daap.sortseriesname
    "ated": ("supportsextradata", "int"),               # daap.supportsextradata
    "asgr": ("supportsgroups", "int"),                  # daap.supportsgroups
    "mscu": ("unknown_cu", "int"),                      # unknown-cu
    "asse": ("unknown_se", "int"),                      # com.apple.itunes.unknown-se
    "capr": ("protocolversion", "str"),                 # dacp.protocolversion
    "caar": ("availablerepeatstates", "int"),           # dacp.availablerepeatstates
    "caas": ("availableshufflestates", "int"),          # dacp.availableshufflestates
    "caci": ("controlint", "str"),                      # dacp.controlint
    "cafe": ("fullscreenenabled", "bool"),              # dacp.fullscreenenabled
    "cafs": ("fullscreen", "bool"),                     # dacp.fullscreen
    "canp": ("nowplayingids", "base64"),                # dacp.nowplayingids
    "canl": ("nowplayingalbum", "str"),                 # dacp.nowplayingalbum
    "cana": ("nowplayingartist", "str"),                # dacp.nowplayingartist
    "cang": ("nowplayinggenre", "str"),                 # dacp.nowplayinggenre
    "cann": ("nowplayingname", "str"),                  # dacp.nowplayingname
    "ceQR": ("playqueue_contents_response", "str"),     # com.apple.itunes.playqueue-contents-response
    "caps": ("playerstate", "int"),                     # dacp.playerstate
    "cant": ("nowplayingtime", "int"),                  # dacp.nowplayingtime
    "cast": ("songtime", "int"),                        # dacp.songtime
    "carp": ("repeatstate", "int"),                     # dacp.repeatstate
    "cash": ("shufflestate", "int"),                    # dacp.shufflestate
    "caia": ("isactive", "bool"),                       # dacp.isactive
    "casp": ("speakers", "str"),                        # dacp.speakers
    "cads": ("unknown_ds", "int"),                      # unknown-ds
    "caip": ("unknown_ip", "int"),                      # com.apple.itunes.unknown-ip
    "caiv": ("unknown_iv", "int"),                      # com.apple.itunes.unknown-iv
    "caks": ("ss", "int"),                              # unknown.ss
    "caov": ("ov", "int"),                              # unknown.ov
    "casa": ("unknown_sa", "int"),                      # com.apple.itunes.unknown-sa
    "casc": ("ss", "int"),                              # unknown.ss
    "cass": ("ss", "int"),                              # unknown.ss
    "casu": ("unknown_su", "int"),                      # com.apple.itunes.unknown-su
    "cavd": ("unknown_vd", "int"),                      # com.apple.itunes.unknown-vd
    "cave": ("visualizerenabled", "bool"),              # dacp.visualizerenabled
    "cavs": ("visualizer", "int"),                      # dacp.visualizer
    "cavc": ("volumecontrollable", "int"),              # dacp.volumecontrollable
    "cmmk": ("mediakind", "int"),                       # dmcp.mediakind
    "cmnm": ("unknown_nm", "str"),                      # unknown-nm
    "cmty": ("unknown_ty", "str"),                      # unknown-ty
    "ceGS": ("genius_selectable", "bool"),              # com.apple.itunes.genius-selectable
    "ceQa": ("playqueue_album", "str"),                 # com.apple.itunes.playqueue-album
    "ceQr": ("playqueue_artist", "str"),                # com.apple.itunes.playqueue-artist
    "ceQg": ("playqueue_genre", "str"),                 # com.apple.itunes.playqueue-genre
    "ceQs": ("playqueue_id", "int"),                    # com.apple.itunes.playqueue-id
    "ceQn": ("playqueue_name", "str"),                  # com.apple.itunes.playqueue-name
    "ceSG": ("saved_genius", "bool"),                   # com.apple.itunes.saved-genius
    "ceQI": ("unknown", "int"),                         # unknown
    "ceSX": ("sx", "int"),                              # unknown.sx
    "ceQh": ("unknown", "str"),                         # unknown
    "ceQi": ("unknown", "int"),                         # unknown
    "ceQk": ("unknown", "str"),                         # unknown
    "ceQl": ("unknown", "str"),                         # unknown
    "ceQm": ("unknown", "int"),                         # unknown
    "ceQS": ("playqueue_content_unknown", "str"),       # com.apple.itunes.playqueue-content-unknown
    "ceQu": ("unknown_Qu", "int"),                      # com.apple.itunes.unknown-Qu
    "cmpr": ("protocolversion", "str"),                 # dmcp.protocolversion
    "cmpa": ("pa", "str"),                              # unknown.pa
    "cmpg": ("unknown_pg", "base64"),                   # com.apple.itunes.unknown-pg
    "cmst": ("playstatus", "str"),                      # dmcp.playstatus
    "cmgt": ("getpropertyresponse", "str"),             # dmcp.getpropertyresponse
    "cmvo": ("volume", "int"),                          # dmcp.volume
    "cmsr": ("serverrevision", "int"),                  # dmcp.serverrevision
    "cmik": ("unknown_ik", "int"),                      # unknown-ik
    "cmrl": ("rl", "int"),                              # unknown.rl
    "cmsp": ("unknown_sp", "int"),                      # unknown-sp
    "cmsv": ("sv", "int"),                              # unknown.sv
    "msau": ("authenticationmethod", "int"),            # dmap.authenticationmethod
    "msas": ("authenticationschemes", "int"),           # dmap.authenticationschemes
    "mbcl": ("bag", "str"),                             # dmap.bag
    "mcon": ("container", "str"),                       # dmap.container
    "mctc": ("containercount", "int"),                  # dmap.containercount
    "mcti": ("containeritemid", "int"),                 # dmap.containeritemid
    "mcna": ("contentcodesname", "str"),                # dmap.contentcodesname
    "mcnm": ("contentcodesnumber", "int"),              # dmap.contentcodesnumber
    "mccr": ("contentcodesresponse", "str"),            # dmap.contentcodesresponse
    "mcty": ("contentcodestype", "int"),                # dmap.contentcodestype
    "msdc": ("databasescount", "int"),                  # dmap.databasescount
    "mdbk": ("databasesharetype", "int"),               # dmap.databasesharetype
    "mudl": ("deletedidlisting", "str"),                # dmap.deletedidlisting
    "mdcl": ("dictionary", "str"),                      # dmap.dictionary
    "mdst": ("downloadstatus", "int"),                  # dmap.downloadstatus
    "meds": ("editcommandssupported", "int"),           # dmap.editcommandssupported
    "mimc": ("itemcount", "int"),                       # dmap.itemcount
    "miid": ("itemid", "int"),                          # dmap.itemid
    "mikd": ("itemkind", "int"),                        # dmap.itemkind
    "minm": ("itemname", "str"),                        # dmap.itemname
    "mlcl": ("listing", "str"),                         # dmap.listing
    "mlit": ("listingitem", "str"),                     # dmap.listingitem
    "mslr": ("loginrequired", "bool"),                  # dmap.loginrequired
    "mlog": ("loginresponse", "str"),                   # dmap.loginresponse
    "mpro": ("protocolversion", "str"),                 # dmap.protocolversion
    "mpco": ("parentcontainerid", "int"),               # dmap.parentcontainerid
    "mper": ("persistentid", "int"),                    # dmap.persistentid
    "mrpr": ("remotepersistentid", "int"),              # dmap.remotepersistentid
    "mrco": ("returnedcount", "int"),                   # dmap.returnedcount
    "msrv": ("serverinforesponse", "str"),              # dmap.serverinforesponse
    "musr": ("serverrevision", "int"),                  # dmap.serverrevision
    "mlid": ("sessionid", "int"),                       # dmap.sessionid
    "mshc": ("sortingheaderchar", "int"),               # dmap.sortingheaderchar
    "mshi": ("sortingheaderindex", "int"),              # dmap.sortingheaderindex
    "mshl": ("sortingheaderlisting", "str"),            # dmap.sortingheaderlisting
    "mshn": ("sortingheadernumber", "int"),             # dmap.sortingheadernumber
    "msma": ("unknown_ma", "int"),                      # com.apple.itunes.unknown-ma
    "mtco": ("specifiedtotalcount", "int"),             # dmap.specifiedtotalcount
    "mstt": ("status", "int"),                          # dmap.status
    "msts": ("statusstring", "str"),                    # dmap.statusstring
    "msal": ("supportsautologout", "bool"),             # dmap.supportsautologout
    "msbr": ("supportsbrowse", "bool"),                 # dmap.supportsbrowse
    "msex": ("supportsextensions", "bool"),             # dmap.supportsextensions
    "msix": ("supportsindex", "bool"),                  # dmap.supportsindex
    "mspi": ("supportspersistentids", "bool"),          # dmap.supportspersistentids
    "msed": ("unknown_ed", "int"),                      # com.apple.itunes.unknown-ed
    "msqy": ("supportsquery", "bool"),                  # dmap.supportsquery
    "msrs": ("supportsresolve", "bool"),                # dmap.supportsresolve
    "msup": ("supportsupdate", "bool"),                 # dmap.supportsupdate
    "mstm": ("timeoutinterval", "int"),                 # dmap.timeoutinterval
    "msml": ("unknown_ml", "str"),                      # com.apple.itunes.unknown-ml
    "mupd": ("updateresponse", "str"),                  # dmap.updateresponse
    "muty": ("updatetype", "int"),                      # dmap.updatetype
    "mstc": ("utctime", "date"),                        # dmap.utctime
    "msto": ("utcoffset", "int"),                       # dmap.utcoffset
    "fch": ("contentcodesresponse", "str"),             # dmap.contentcodesresponse
    "____": ("req_fplay", "int"),                       # com.apple.itunes.req-fplay
    "ceVO": ("unknown_voting", "int"),                  # com.apple.itunes.unknown-voting
    "pasp": ("aspectratio", "str"),                     # dpap.aspectratio
    "picd": ("creationdate", "date"),                   # dpap.creationdate
    "peak": ("album_kind", "int"),                      # com.apple.itunes.photos.album-kind
    "peed": ("exposure_date", "date"),                  # com.apple.itunes.photos.exposure-date
    "pefc": ("faces", "str"),                           # com.apple.itunes.photos.faces
    "peki": ("key_image_id", "int"),                    # com.apple.itunes.photos.key-image-id
    "pemd": ("modification_date", "date"),              # com.apple.itunes.photos.modification-date
    "pfai": ("failureids", "str"),                      # dpap.failureids
    "pfdt": ("filedata", "base64"),                     # dpap.filedata
    "pcmt": ("imagecomments", "str"),                   # dpap.imagecomments
    "pimf": ("imagefilename", "str"),                   # dpap.imagefilename
    "pifs": ("imagefilesize", "int"),                   # dpap.imagefilesize
    "pfmt": ("imageformat", "str"),                     # dpap.imageformat
    "plsz": ("imagelargefilesize", "int"),              # dpap.imagelargefilesize
    "phgt": ("imagepixelheight", "int"),                # dpap.imagepixelheight
    "pwth": ("imagepixelwidth", "int"),                 # dpap.imagepixelwidth
    "prat": ("imagerating", "int"),                     # dpap.imagerating
    "ppro": ("protocolversion", "str"),                 # dpap.protocolversion
    "pret": ("retryids", "str"),                        # dpap.retryids
    "ipsa": ("iphotoslideshowadvancedoptions", "str"),  # dpap.iphotoslideshowadvancedoptions
    "ipsl": ("iphotoslideshowoptions", "str"),          # dpap.iphotoslideshowoptions
    "aeFA": ("drm_family_id", "int"),                   # com.apple.itunes.drm-family-id
    "aeDL": ("drm_downloader_user_id", "int"),          # com.apple.itunes.drm-downloader-user-id

    # Unknown codes. Let me know, if you know what they mean
    "meia": ("unknown_meia", "int"),                    # ?
    "meip": ("unknown_meip", "int"),                    # ?
    "mext": ("unknown_mext", "int"),                    # ?
    "ajal": ("unknown_ajal", "int"),                    # ?
    "ajcA": ("unknown_ajca", "int"),                    # ?
    "awrk": ("unknown_awrk", None),                     # ?
    "amvm": ("unknown_amvm", None),                     # ?
    "amvc": ("unknown_amvc", "int"),                    # ?
    "amvn": ("unknown_amvn", "int"),                    # ?
    "ajuw": ("unknown_ajuw", "int"),                    # ?
    "ajAV": ("unknown_ajAV", "int"),                    # ?
    "ajAT": ("unknown_ajAT", "int"),                    # ?
    "ajAE": ("unknown_ajAE", "int"),                    # ?
    "ajAS": ("unknown_ajAS", "int"),                    # ?
}


# shairport-sync codes
SSNC_CODE_DICT = {
    "pcst": ("picturestart", "int"),  # with rtptime
    "pcen": ("pictureend", "int"),    # with rtptime
    "PICT": ("artwork", "bytes"),
    "mdst": ("metadatastart", None),
    "mden": ("metadataend", None),
    # see https://github.com/mikebrady/shairport-sync-metadata-reader/issues/5
    "pbeg": ("streambegin", None),
    "pfls": ("streampause", None),
    "prsm": ("streamstartresume", None),
    "pend": ("streamstop", None),
    # current playback position / end
    "prgr": ("playbackprogress", lambda item: [float(i) for i in item.data_str.split("/")]),
    # "airplay_volume,volume,lowest_volume,highest_volume"
    # where "volume", "lowest_volume" and "highest_volume" are given in dB.
    # The "airplay_volume" is send by the source (e.g. iTunes) to the player
    # and its range starts from 0.00 down to -30.00, whereby -144.00 means "mute".
    "pvol": ("playbackvolume", lambda item: [float(i) for i in item.data_str.split(",")]),
    "daid": ("dacpid", "str"),  # DACP-ID
    "acre": ("active", "str"),  # Active Remote token
    "snua": ("useragent", "str"),
    "flsr": ("flushrequested", None),
    "pffr": ("firstframreceived", None),
    "dapo": ("clientportnumber", "str"),
    "clip": ("clientipaddress", "str"),
    "svip": ("serveripaddress", "str"),
    "snam": ("sourcename", "str")
}
