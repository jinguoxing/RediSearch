from RLTest import Env


def testDictAdd():
    env = Env()
    env.Expect('ft.dictadd', 'dict', 'term1', 'term2', 'term3').Equal(3)
    env.Expect('ft.dictadd', 'dict', 'term1', 'term2', 'term4').Equal(1)


def testDictAddWrongArity():
    env = Env()
    env.Expect('ft.dictadd', 'dict').RaiseError()


def testDictDelete():
    env = Env()
    env.Expect('ft.dictadd', 'dict', 'term1', 'term2', 'term3').Equal(3)
    env.Expect('ft.dictdel', 'dict', 'term1', 'term2', 'term4').Equal(2)
    env.Expect('ft.dictdel', 'dict', 'term3').Equal(1)
    env.Expect('keys', '*').Equal([])


def testDictDeleteWrongArity():
    env = Env()
    env.Expect('ft.dictdel', 'dict').RaiseError()


def testDictDeleteOnNoneExistingKey():
    env = Env()
    env.Expect('ft.dictdel', 'dict', 'term1').Equal(0)


def testDictDump():
    env = Env()
    env.Expect('ft.dictadd', 'dict', 'term1', 'term2', 'term3').Equal(3)
    env.Expect('ft.dictdump', 'dict').Equal(['term1', 'term2', 'term3'])


def testDictDumpWrongArity():
    env = Env()
    env.Expect('ft.dictdump').RaiseError()


def testDictDumpOnNoneExistingKey():
    env = Env()
    env.Expect('ft.dictdump', 'dict').RaiseError()


def testBasicSpellCheck():
    env = Env()
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'name1', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'name2', 'body', 'body2')
    env.cmd('ft.add', 'idx', 'doc3', 1.0, 'FIELDS', 'name', 'name2', 'body', 'name2')
    env.Expect('ft.spellcheck', 'idx', 'name').Equal([['TERM', 'name',
                                                       [['0.66666666666666663', 'name2'], ['0.33333333333333331', 'name1']]]])
    if not env.IsCluster():
        env.Expect('ft.spellcheck', 'idx', '@body:name').Equal([['TERM', 'name', [['0.66666666666666663', 'name2']]]])


def testBasicSpellCheckWithNoResult():
    env = Env()
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'name1', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'name2', 'body', 'body2')
    env.cmd('ft.add', 'idx', 'doc3', 1.0, 'FIELDS', 'name', 'name2', 'body', 'name2')
    env.Expect('ft.spellcheck', 'idx', 'somenotexiststext').Equal([['TERM', 'somenotexiststext', []]])


def testSpellCheckOnExistingTerm():
    env = Env()
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'name', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'name2', 'body', 'body2')
    env.cmd('ft.add', 'idx', 'doc3', 1.0, 'FIELDS', 'name', 'name2', 'body', 'name2')
    env.Expect('ft.spellcheck', 'idx', 'name').Equal([])


def testSpellCheckWithIncludeDict():
    env = Env()
    env.cmd('ft.dictadd', 'dict', 'name3', 'name4', 'name5')
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'name1', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'name2', 'body', 'body2')
    env.cmd('ft.add', 'idx', 'doc3', 1.0, 'FIELDS', 'name', 'name2', 'body', 'name2')
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'INCLUDE', 'dict').Equal([['TERM', 'name',
                                                                                   [['0.66666666666666663', 'name2'],
                                                                                    ['0.33333333333333331', 'name1'],
                                                                                    ['0', 'name3'], ['0', 'name4'],
                                                                                    ['0', 'name5']]]])
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'include', 'dict').Equal([['TERM', 'name',
                                                                                   [['0.66666666666666663', 'name2'],
                                                                                    ['0.33333333333333331', 'name1'],
                                                                                    ['0', 'name3'], ['0', 'name4'],
                                                                                    ['0', 'name5']]]])


def testSpellCheckWithDuplications():
    env = Env()
    env.cmd('ft.dictadd', 'dict', 'name1', 'name4', 'name5')
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'name1', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'name2', 'body', 'body2')
    env.cmd('ft.add', 'idx', 'doc3', 1.0, 'FIELDS', 'name', 'name2', 'body', 'name2')
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'INCLUDE', 'dict').Equal([['TERM', 'name',
                                                                                   [['0.66666666666666663', 'name2'],
                                                                                    ['0.33333333333333331', 'name1'],
                                                                                    ['0', 'name4'], ['0', 'name5']]]])


def testSpellCheckExcludeDict():
    env = Env()
    env.cmd('ft.dictadd', 'dict', 'name')
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'name1', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'name2', 'body', 'body2')
    env.cmd('ft.add', 'idx', 'doc3', 1.0, 'FIELDS', 'name', 'name2', 'body', 'name2')
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'EXCLUDE', 'dict').Equal([])
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'exclude', 'dict').Equal([])


def testSpellCheckNoneExistingIndex():
    env = Env()
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'EXCLUDE', 'dict').RaiseError()


def testSpellCheckWrongArity():
    env = Env()
    env.cmd('ft.dictadd', 'dict', 'name')
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'name1', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'name2', 'body', 'body2')
    env.cmd('ft.add', 'idx', 'doc3', 1.0, 'FIELDS', 'name', 'name2', 'body', 'name2')
    env.Expect('ft.spellcheck', 'idx').RaiseError()
    env.Expect('ft.spellcheck', 'idx').RaiseError()


def testSpellCheckBadFormat():
    env = Env()
    env.cmd('ft.dictadd', 'dict', 'name')
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'name1', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'name2', 'body', 'body2')
    env.cmd('ft.add', 'idx', 'doc3', 1.0, 'FIELDS', 'name', 'name2', 'body', 'name2')
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS').RaiseError()
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'INCLUDE').RaiseError()
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'EXCLUDE').RaiseError()
    env.Expect('ft.spellcheck', 'idx', 'name', 'DISTANCE').RaiseError()
    env.Expect('ft.spellcheck', 'idx', 'name', 'DISTANCE', 0).RaiseError()
    env.Expect('ft.spellcheck', 'idx', 'name', 'DISTANCE', -1).RaiseError()
    env.Expect('ft.spellcheck', 'idx', 'name', 'DISTANCE', 101).RaiseError()


def testSpellCheckNoneExistingDicts():
    env = Env()
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'name1', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'name2', 'body', 'body2')
    env.cmd('ft.add', 'idx', 'doc3', 1.0, 'FIELDS', 'name', 'name2', 'body', 'name2')
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'INCLUDE', 'dict').RaiseError()
    env.Expect('ft.spellcheck', 'idx', 'name', 'TERMS', 'EXCLUDE', 'dict').RaiseError()


def testSpellCheckResultsOrder():
    env = Env()
    env.cmd('ft.dictadd', 'dict', 'name')
    env.cmd('ft.create', 'idx', 'SCHEMA', 'name', 'TEXT', 'body', 'TEXT')
    env.cmd('ft.add', 'idx', 'doc1', 1.0, 'FIELDS', 'name', 'Elior', 'body', 'body1')
    env.cmd('ft.add', 'idx', 'doc2', 1.0, 'FIELDS', 'name', 'Hila', 'body', 'body2')
    env.Expect('ft.spellcheck', 'idx', 'Elioh Hilh').Equal([['TERM', 'elioh', [['0.5', 'elior']]], ['TERM', 'hilh', [['0.5', 'hila']]]])


def testSpellCheckIssue437():
    env = Env()
    env.cmd('ft.create', 'incidents', 'SCHEMA', 'report', 'text')
    env.cmd('FT.DICTADD', 'slang', 'timmies', 'toque', 'toonie', 'serviette', 'kerfuffle', 'chesterfield')
    env.Expect('FT.SPELLCHECK', 'incidents',
               'Tooni toque kerfuffle', 'TERMS',
               'EXCLUDE', 'slang', 'TERMS',
               'INCLUDE', 'slang').Equal([['TERM', 'tooni', [['0', 'toonie']]]])
