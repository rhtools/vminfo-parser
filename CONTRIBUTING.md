# Contributing

## Conventional Commits

All commits on `dev` and `main` must follow the [Conventional Commit Standard](https://www.conventionalcommits.org/en/v1.0.0/).
The following types are supported:

* chore - Dependancy Security Updates, Merges, Cleanup.
* ci - Changes to CI/CD workflows
* docs - Changes to Documentations
* feat - New Features or Feature Enhancements
* fix - Bugfixes (should linked to an issue)
* perf - Perfomance Enhancements
* style - Code Style Changes
* refactor - Refactor of code for maintenance reasons (should use feat or perf if appopriate)
* test - Changes to Tests.  

While not explicityly required for individual commits that will be squash merged into dev,  it is advantagous to follow the standard for consistentency.

## PRs

All Pull requests should be opened against the `dev` branch.
All PRs titles must conform to the conventional commit standards.
All Merges into `dev` should be accomplished with squash merges,  with the PR title as the commit message.
Because of this, All PRs should cover a single change.
Shoehorning other changes into a PR will make this disappear from the release notes and make them difficult to revert.  

When PRs are merged into `dev` a prerelease will be built with with the appropriate semantic version based on the commit message along with a `-dev` tag.

## Releases

Releases will be accomplished by PR from `dev` to `main`.
The PRs will be Merged to `main` retaining all the presumably Conventional Commit compliant commits, for use with generating semanatic version.
Merges into `main` will automatically trigger a release with a semantic version based on the commits pushed.  

## Testing

All tests are executed by `pytest`.  

Testing requirements are stored in [tests/requirements.txt](requirements.txt), and supplements the [development](../dev-requirements.txt) and [execution requirements](../requirements.txt).  Testing and Execution requirements must be installed for testing.

```sh
pip isntall -r requirements.txt
pip install -r tests/requirements.txt
```

alternatively,  if using editable installs

```sh
pip install -e ".[test,dev]"
```

Assuming dependancies are installed as above, tests can be executed with:

```sh
pytest
```

Individual test files can be run by adding the file path to the command.  For example, to only run the tests in test_config.py

```sh
pytest tests/test_config.py
```

### Image Comparison

Plots are tested using `pytest-mpl` using hash and image comparison.  

When changes are made, or new tests are added, baseline images and hashes must be generated/updated before the tests will pass.

Baseline images as well as hashes are stored in [tests/images/](tests/images)

The following command can be run prior to commit in order to generate these.

```sh
pytest --mpl-generate-path=tests/images --mpl-generate-hash-library=tests/images/hashes.json tests/unit/test_visualizer.py
```

### Test Output

E2E tests write output to [tests/outputs](tests/outputs/).
This can be used for manual comparison or for manually updating the expected output in [tests/const.py](tests/const.py).

### Test Profile

E2E tests collect a profile using [cProfile](https://docs.python.org/3/library/profile.html#module-cProfile).
This profile is saved next to stdout in [tests/const.py](tests/const.py).
This profile included time and count for all calls made by main recursively.
This data is stored in a binary form and must be loaded by `pstats.Stats` in order to be read.

```python
from pstats import Stats

s = Stats("tests/outputs/tests/e2e/test_main.py::test_main_with_args[disk_space_by_os]/profile")

s.sort_stats('cumulative') # sort by cumalative runtime (call to return, inclusive of anything it calls)

s.print_stats(0.1) # print the top 10% of calls (.i.e. highest cumulative runtime)

Wed Oct 30 15:46:06 2024    tests/outputs/tests/e2e/test_main.py::test_main_with_args[disk_space_by_os]/profile

         24100301 function calls (23877019 primitive calls) in 10.351 seconds

   Ordered by: cumulative time
   List reduced from 1435 to 144 due to restriction <0.1>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   10.351   10.351 {built-in method builtins.exec}
        1    0.002    0.002   10.351   10.351 <string>:1(<module>)
        1    0.000    0.000   10.349   10.349 vminfo_parser/__main__.py:154(main)
        1    0.000    0.000    5.340    5.340 vminfo_parser/vmdata.py:37(from_file)
        1    0.000    0.000    5.339    5.339 pandas/io/excel/_base.py:451(read_excel)
        1    0.000    0.000    5.330    5.330 pandas/io/excel/_base.py:1576(parse)
        1    0.001    0.001    5.330    5.330 pandas/io/excel/_base.py:719(parse)
        1    1.150    1.150    5.289    5.289 pandas/io/excel/_openpyxl.py:607(get_sheet_data)
        1    0.000    0.000    4.656    4.656 vminfo_parser/__main__.py:112(show_disk_space_by_os)
        1    0.000    0.000    4.656    4.656 vminfo_parser/analyzer.py:476(by_os)
       23    0.002    0.000    4.655    0.202 vminfo_parser/__main__.py:124(show_disk_space)
       23    0.028    0.001    4.640    0.202 vminfo_parser/analyzer.py:263(get_disk_space)
  1048577    0.224    0.000    3.616    0.000 openpyxl/worksheet/_read_only.py:60(_cells_by_row)
    58480    0.367    0.000    2.960    0.000 openpyxl/worksheet/_reader.py:125(parse)
       23    0.056    0.002    2.556    0.111 vminfo_parser/analyzer.py:99(calculate_disk_space_ranges)
    52616    0.053    0.000    2.139    0.000 pandas/core/frame.py:1505(iterrows)
53873/53872    0.308    0.000    2.000    0.000 pandas/core/series.py:389(__init__)
       23    0.003    0.000    1.896    0.082 vminfo_parser/vmdata.py:167(create_environment_filtered_dataframe)
       23    0.000    0.000    1.778    0.077 pandas/core/series.py:4789(apply)
       23    0.000    0.000    1.777    0.077 pandas/core/apply.py:1409(apply)
       23    0.000    0.000    1.777    0.077 pandas/core/apply.py:1482(apply_standard)
       46    0.000    0.000    1.775    0.039 pandas/core/base.py:891(_map_values)
       46    0.204    0.004    1.774    0.039 pandas/core/algorithms.py:1667(map_array)
  1266702    0.607    0.000    1.569    0.000 pandas/core/apply.py:1495(curried)
    58479    0.284    0.000    1.375    0.000 openpyxl/worksheet/_reader.py:282(parse_row)
824729/824728    0.178    0.000    1.181    0.000 /xml/etree/ElementTree.py:1233(iterator)
   383034    0.583    0.000    1.045    0.000 openpyxl/worksheet/_reader.py:189(parse_cell)
  1266702    0.465    0.000    0.962    0.000 vminfo_parser/vmdata.py:193(_categorize_environment)
    54319    0.191    0.000    0.654    0.000 pandas/core/construction.py:517(sanitize_array)
     1432    0.124    0.000    0.519    0.000 /xml/etree/ElementTree.py:1278(feed)
  1267769    0.261    0.000    0.513    0.000 pandas/core/dtypes/missing.py:101(isna)
   826163    0.331    0.000    0.450    0.000 /xml/etree/ElementTree.py:1302(read_events)
    58479    0.247    0.000    0.433    0.000 openpyxl/worksheet/_read_only.py:105(_get_row)
   385525    0.333    0.000    0.417    0.000 pandas/io/excel/_openpyxl.py:589(_convert_cell)
     1438    0.395    0.000    0.395    0.000 {method 'feed' of 'xml.etree.ElementTree.XMLParser' objects}
2898183/2896778    0.233    0.000    0.303    0.000 {built-in method builtins.isinstance}
    53872    0.066    0.000    0.265    0.000 pandas/core/internals/managers.py:1863(from_array)
    52593    0.071    0.000    0.256    0.000 pandas/core/series.py:1095(__getitem__)
  1267769    0.237    0.000    0.252    0.000 pandas/core/dtypes/missing.py:184(_isna)
    52935    0.138    0.000    0.237    0.000 pandas/core/dtypes/cast.py:1156(maybe_infer_to_datetimelike)
   383034    0.233    0.000    0.233    0.000 openpyxl/utils/cell.py:206(coordinate_to_tuple)
    56598    0.060    0.000    0.229    0.000 pandas/core/generic.py:6301(__setattr__)
   383034    0.142    0.000    0.186    0.000 openpyxl/cell/read_only.py:14(__init__)
        1    0.002    0.002    0.186    0.186 vminfo_parser/vmdata.py:80(add_extra_columns)
       49    0.001    0.000    0.167    0.003 pandas/core/strings/accessor.py:129(wrapper)
    53904    0.033    0.000    0.167    0.000 pandas/_config/config.py:145(_get_option)
        1    0.000    0.000    0.165    0.165 vminfo_parser/vmdata.py:189(save_to_csv)
        1    0.000    0.000    0.165    0.165 pandas/util/_decorators.py:325(wrapper)
        1    0.000    0.000    0.165    0.165 pandas/core/generic.py:3797(to_csv)
        1    0.000    0.000    0.165    0.165 pandas/io/formats/format.py:965(to_csv)
        1    0.000    0.000    0.165    0.165 pandas/io/formats/csvs.py:246(save)
        1    0.000    0.000    0.164    0.164 pandas/io/formats/csvs.py:272(_save)
        1    0.002    0.002    0.164    0.164 pandas/io/formats/csvs.py:305(_save_body)
        7    0.105    0.015    0.162    0.023 pandas/io/formats/csvs.py:315(_save_chunk)
        3    0.001    0.000    0.162    0.054 pandas/core/strings/accessor.py:2649(extract)
    53965    0.043    0.000    0.154    0.000 pandas/core/generic.py:807(_set_axis)
        3    0.029    0.010    0.151    0.050 pandas/core/strings/object_array.py:474(_str_extract)
    54459    0.095    0.000    0.140    0.000 pandas/core/generic.py:6236(__finalize__)
947497/726537    0.093    0.000    0.132    0.000 {built-in method builtins.len}
   165222    0.073    0.000    0.122    0.000 pandas/core/strings/object_array.py:488(f)
    52593    0.043    0.000    0.118    0.000 pandas/core/series.py:1220(_get_value)
    54937    0.032    0.000    0.114    0.000 pandas/core/series.py:784(name)
       81    0.000    0.000    0.112    0.001 pandas/core/generic.py:6662(copy)
       81    0.000    0.000    0.111    0.001 pandas/core/internals/managers.py:557(copy)
  1149119    0.108    0.000    0.108    0.000 {method 'get' of 'xml.etree.ElementTree.Element' objects}
     1064    0.001    0.000    0.107    0.000 pandas/core/ops/common.py:62(new_method)
    53904    0.046    0.000    0.099    0.000 pandas/_config/config.py:127(_get_single_key)
      236    0.001    0.000    0.093    0.000 pandas/core/internals/managers.py:317(apply)
    53965    0.017    0.000    0.087    0.000 pandas/core/internals/managers.py:236(set_axis)
  1096475    0.084    0.000    0.084    0.000 openpyxl/cell/read_only.py:108(value)
    54049    0.045    0.000    0.084    0.000 pandas/core/internals/blocks.py:2645(maybe_coerce_values)
    53250    0.055    0.000    0.083    0.000 numpy/_core/numeric.py:303(full)
    54937    0.019    0.000    0.082    0.000 pandas/core/dtypes/common.py:1571(validate_all_hashable)
    54607    0.068    0.000    0.082    0.000 pandas/core/generic.py:278(__init__)
      717    0.001    0.000    0.082    0.000 pandas/core/series.py:6110(_cmp_method)
    53929    0.038    0.000    0.080    0.000 pandas/core/internals/blocks.py:2716(new_block)
       65    0.016    0.000    0.080    0.001 pandas/core/internals/managers.py:1782(_consolidate_inplace)
  1052635    0.076    0.000    0.076    0.000 {method 'append' of 'list' objects}
    53965    0.021    0.000    0.070    0.000 pandas/core/internals/base.py:86(_validate_set_axis)
   122008    0.035    0.000    0.069    0.000 pandas/core/dtypes/generic.py:42(_instancecheck)
   383034    0.066    0.000    0.066    0.000 {method 'findtext' of 'xml.etree.ElementTree.Element' objects}
     1138    0.003    0.000    0.064    0.000 pandas/core/frame.py:4062(__getitem__)
       39    0.000    0.000    0.063    0.002 pandas/core/internals/managers.py:2259(_consolidate)
55220/55211    0.022    0.000    0.063    0.000 {built-in method builtins.all}
   824726    0.061    0.000    0.061    0.000 {method 'popleft' of 'collections.deque' objects}
       99    0.039    0.000    0.061    0.001 pandas/core/internals/managers.py:2276(_merge_blocks)
       57    0.001    0.000    0.056    0.001 pandas/core/indexes/base.py:7770(get_values_for_csv)
        7    0.000    0.000    0.055    0.008 pandas/core/frame.py:1400(_get_values_for_csv)
        7    0.000    0.000    0.055    0.008 pandas/core/internals/managers.py:459(get_values_for_csv)
   220286    0.055    0.000    0.055    0.000 openpyxl/worksheet/_reader.py:80(_cast_number)
       49    0.000    0.000    0.055    0.001 pandas/core/internals/blocks.py:775(get_values_for_csv)
    57491    0.020    0.000    0.053    0.000 pandas/core/series.py:734(name)
   219257    0.038    0.000    0.052    0.000 pandas/core/indexes/base.py:909(__len__)
    54296    0.029    0.000    0.051    0.000 pandas/core/construction.py:696(_sanitize_ndim)
     1064    0.002    0.000    0.051    0.000 pandas/core/series.py:6201(_construct_result)
     1191    0.049    0.000    0.049    0.000 {method 'astype' of 'numpy.ndarray' objects}
       23    0.001    0.000    0.048    0.002 vminfo_parser/analyzer.py:198(sort_by_disk_space_range)
      246    0.001    0.000    0.048    0.000 pandas/core/frame.py:4130(_getitem_bool_array)
    54250    0.031    0.000    0.047    0.000 pandas/core/indexing.py:2765(check_dict_or_set_indexers)
   409867    0.046    0.000    0.046    0.000 {method 'startswith' of 'str' objects}
   383034    0.045    0.000    0.045    0.000 openpyxl/cell/read_only.py:112(value)
    53957    0.015    0.000    0.044    0.000 pandas/core/common.py:568(require_length_match)
      717    0.002    0.000    0.043    0.000 pandas/core/ops/array_ops.py:288(comparison_op)
    54113    0.030    0.000    0.042    0.000 pandas/core/internals/blocks.py:2674(get_block_type)
    54750    0.015    0.000    0.041    0.000 pandas/core/series.py:831(_values)
   109874    0.023    0.000    0.041    0.000 pandas/core/dtypes/common.py:1590(<genexpr>)
        1    0.000    0.000    0.041    0.041 pandas/io/parsers/readers.py:1907(read)
      124    0.001    0.000    0.039    0.000 pandas/core/indexing.py:882(__setitem__)
    54764    0.034    0.000    0.039    0.000 pandas/core/generic.py:6284(__getattr__)
    54282    0.020    0.000    0.038    0.000 pandas/core/indexes/base.py:7688(maybe_extract_name)
        1    0.000    0.000    0.037    0.037 pandas/io/parsers/python_parser.py:246(read)
    53189    0.031    0.000    0.037    0.000 pandas/core/indexes/base.py:3777(get_loc)
   107902    0.029    0.000    0.037    0.000 pandas/core/indexes/base.py:7593(ensure_index)
    58572    0.037    0.000    0.037    0.000 {method 'clear' of 'xml.etree.ElementTree.Element' objects}
     1025    0.036    0.000    0.036    0.000 {method 'copy' of 'numpy.ndarray' objects}
   157834    0.036    0.000    0.036    0.000 {method 'search' of 're.Pattern' objects}
    53904    0.028    0.000    0.035    0.000 pandas/_config/config.py:635(_get_root)
     1441    0.004    0.000    0.035    0.000 /zipfile/__init__.py:964(read)
    53904    0.024    0.000    0.035    0.000 pandas/_config/config.py:676(_translate_key)
       23    0.000    0.000    0.035    0.002 pandas/core/arraylike.py:38(__eq__)
   110600    0.027    0.000    0.035    0.000 pandas/core/dtypes/inference.py:334(is_hashable)
   122008    0.026    0.000    0.034    0.000 pandas/core/dtypes/generic.py:37(_check)
      240    0.001    0.000    0.034    0.000 pandas/core/generic.py:4142(_take_with_is_copy)
       23    0.033    0.001    0.033    0.001 pandas/core/ops/array_ops.py:113(comp_method_OBJECT_ARRAY)
      240    0.001    0.000    0.032    0.000 pandas/core/generic.py:4027(take)
     1439    0.006    0.000    0.031    0.000 /zipfile/__init__.py:1046(_read1)
      272    0.000    0.000    0.031    0.000 pandas/core/internals/blocks.py:790(copy)
      254    0.001    0.000    0.031    0.000 pandas/core/internals/managers.py:869(take)
     2525    0.012    0.000    0.030    0.000 {built-in method builtins.max}
  147/124    0.001    0.000    0.028    0.000 pandas/core/indexing.py:1785(_setitem_with_indexer)
    56405    0.025    0.000    0.028    0.000 pandas/core/construction.py:481(ensure_wrapped_if_datetimelike)
      278    0.002    0.000    0.028    0.000 pandas/core/internals/managers.py:623(reindex_indexer)
    54750    0.020    0.000    0.026    0.000 pandas/core/internals/managers.py:2004(internal_values)
      347    0.000    0.000    0.024    0.000 pandas/core/arraylike.py:58(__ge__)
  112/103    0.001    0.000    0.024    0.000 pandas/core/frame.py:4271(__setitem__)
     1692    0.002    0.000    0.024    0.000 pandas/core/internals/blocks.py:1287(take_nd)
    55546    0.019    0.000    0.023    0.000 pandas/core/construction.py:416(extract_array)
      347    0.000    0.000    0.023    0.000 pandas/core/arraylike.py:50(__le__)
      347    0.000    0.000    0.023    0.000 pandas/core/arraylike.py:68(__and__)
      347    0.001    0.000    0.023    0.000 pandas/core/series.py:6123(_logical_method)
   294898    0.023    0.000    0.023    0.000 {built-in method builtins.getattr}
      109    0.000    0.000    0.023    0.000 pandas/core/frame.py:4514(_set_item)
       45    0.022    0.000    0.022    0.000 numpy/_core/shape_base.py:221(vstack)
     1809    0.002    0.000    0.022    0.000 pandas/core/array_algos/take.py:59(take_nd)

# NOTE: above output is modified to remove library paths to make it easier to read.
# actual output looks like :
#  1    0.000    0.000    0.000    0.000 /Users/jaross/work/ocpv/vminfo_parser/vminfo_parser/analyzer.py:17(__init__)
```

This can be used to help understand execution time and improve performance.
Added test time is negligible,  so will be left in even when not used.