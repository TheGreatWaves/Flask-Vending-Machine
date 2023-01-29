from app.utils.log import Log, Record
from app.utils.result import Result


def test_empty_record():
    empty_record: Record = Record()
    assert empty_record.records == {}


def test_iadd_record():
    record_1: Record = Record({"Aliens": ["Are they real?"]})
    record_2: Record = Record({"Aliens": ["Who knows"]})
    record_3: Record = Record({"Atlantis": ["Definitely not real right...?"]})

    # Add existing
    record_1 += record_2
    assert record_1.records.get("Aliens") == ["Are they real?", "Who knows"]

    record_1 += record_3
    assert record_1.records.get("Atlantis") == record_3.records.get("Atlantis")


def test_add_records():
    empty_record: Record = Record()

    # empty
    assert empty_record.records == {}

    # test adding
    empty_record.add(specific="Aliens", new_record="Probably real?")
    assert empty_record.records.get("Aliens") == ["Probably real?"]


def test_empty_log():
    empty_log: Log = Log()
    assert empty_log.logs == {}


def test_copy_log():
    copy_from_log: Log = Log(
        log={"Weird words": Record(records={"Foo": ["Wow that is really weird."]})}
    )

    assert copy_from_log.has_entry(broad="Weird words", specific="Foo")


def test_entry_log():
    log: Log = Log()

    supernatural_discussions = log.entry("Supernatural Discussions")
    _ = log.entry("Forgotten Discussions")

    assert "Supernatural Discussions" in log.logs

    assert len(supernatural_discussions.records) == 0

    supernatural_discussions.add(specific="Aliens", new_record="I think they're real.")

    assert len(supernatural_discussions.records) == 1

    supernatural_discussions.add(
        specific="Aliens", new_record="I think you are onto something."
    )

    assert len(supernatural_discussions.records.get("Aliens")) == 2

    weird_discussions = log.entry("Forgotten Discussions")
    weird_discussions.add(specific="Why are we here?", new_record="Who knows. Foo.")

    assert len(weird_discussions.records.get("Why are we here?")) == 1


def test_add_result():
    log: Log = Log()

    attack_result = Result.error("TooWeakError")
    log.add_result(
        name="Attack", specific="Slap", result=attack_result, err_name="AttackFailed"
    )

    assert log.has_error("AttackFailed")

    attack_result = Result.error("TooWeakError")
    log.add_result(name="Attack", specific="Kick", result=attack_result)

    assert log.has_error("Kick")


def test_iadd_log():
    log_1: Log = Log(
        {"Weird Topics": Record({"Atlantis": ["I've seen atlantis, trust me!"]})}
    )
    log_2: Log = Log(
        {"Weird Topics": Record({"Aliens": ["What? It's just an air balloon."]})}
    )
    log_3: Log = Log({"Weird Topics": Record({"Aliens": ["Not this again..."]})})
    log_4: Log = Log({"Weird People": Record({"John": ["Yeah that is really odd."]})})

    log_1 += log_2

    assert log_1.has_entry(broad="Weird Topics", specific="Aliens")

    assert log_1.has_entry(broad="Weird Topics", specific="Atlantis")

    log_2 += log_3

    assert log_2.logs.get("Weird Topics").get("Aliens") == [
        "What? It's just an air balloon.",
        "Not this again...",
    ]

    log_1 += log_4

    assert log_1.has_entry(broad="Weird People", specific="John")
    assert log_1.logs.get("Weird People").get("John") == ["Yeah that is really odd."]


def test_has_entry():
    log_1: Log = Log(
        {"Weird Topics": Record({"Atlantis": ["I've seen atlantis, trust me!"]})}
    )

    assert log_1.has_entry(broad="Weird Topics")
    assert log_1.has_entry(broad="Weird Topics", specific="Atlantis")
    assert not log_1.has_entry(broad="Weird Topics", specific="Aliens")
    assert not log_1.has_entry(broad="Random topic", specific="John")
