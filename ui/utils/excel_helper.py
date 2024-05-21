import os
import traceback

import xlrd

from ui.entity.case_data import CaseData
from ui.entity.sub_case_data import SubCaseData
from ui.entity.block_data import BlockingData
from ui.utils.log import Logging
from ui.utils import constant

class ExcelHelper(object):
    def __init__(self, path, sheet_name):
        self.path = path
        self.sheet_name = sheet_name
        self.is_screenshot = False

    def __fetch_merged_cells(self, sheet):
        merged_dict = {}
        if not sheet.merged_cells:
            return merged_dict
        for item in sheet.merged_cells:
            if int(item[2]) == 0 and int(item[3]) == 1:
                start = int(item[0])
                end = int(item[1])
                length = end - start
                merged_dict.update({(start + 1, end): length}) 
        return merged_dict

    def get_sub_case_data(self):
        if self.path:
            all_data = []
            sheet = self.get_sheet(self.path, self.sheet_name)
            # merged_dict = self.__fetch_merged_cells(sheet)
            # print(merged_dict)
            header_dict = {}
            try:
                for row_index in range(sheet.nrows):
                    sub_cd = SubCaseData()
                    blocking_data = BlockingData() 
                    row_current = []
                    for col_index in range(sheet.ncols):
                        value = self.get_cell_value(col_index, row_index, sheet)
                        if row_index == 0:
                            header_dict[col_index] = value
                        else:
                            row_current.append(value)
                            if header_dict[col_index] == 'step_id':
                                # print('row_index: {}, col_index:{}, step id: {}'.format(row_index, col_index, value))
                                if value:
                                    sub_cd.step_id = int(value)
                                    # if step id not empty, always set is_screenshot to False
                                    self.is_screenshot = False
                            elif header_dict[col_index] == 'step_desc':
                                if value:
                                    sub_cd.step_desc = value
                            elif header_dict[col_index] == 'test_action':
                                if value:
                                    sub_cd.test_action = value
                                    if value.lower() == 'screenshot':
                                        self.is_screenshot = True 
                                    else:
                                        self.is_screenshot = False
                            elif header_dict[col_index] == 'test_control_type':
                                if not self.is_screenshot:
                                    sub_cd.test_control_type = value
                                else:
                                    blocking_data.test_control_type = value
                            elif header_dict[col_index] == 'test_control':
                                if not self.is_screenshot:
                                    sub_cd.test_control = value
                                else:
                                    blocking_data.test_control = value
                            elif header_dict[col_index] == 'ios_control_type':
                                if not self.is_screenshot:
                                    sub_cd.ios_control_type = value
                                else:
                                    blocking_data.ios_control_type = value
                            elif header_dict[col_index] == 'ios_control':
                                if not self.is_screenshot:
                                    sub_cd.ios_control = value
                                else:
                                    blocking_data.ios_control = value
                            elif header_dict[col_index] == 'test_text':
                                if not self.is_screenshot:
                                    sub_cd.test_text = value
                            elif header_dict[col_index] == 'test_range':
                                if not self.is_screenshot:
                                    sub_cd.test_range = value
                            elif header_dict[col_index] == 'test_wait':
                                if not self.is_screenshot:
                                    sub_cd.test_wait = value
                            elif header_dict[col_index] == 'screen_shot':
                                if not self.is_screenshot:
                                    sub_cd.screen_shot = value
                            elif header_dict[col_index] == 'ignore_exception':
                                sub_cd.ignore_exception = value
                    if row_index != 0:
                        # if current step is not screenshot, just add current step to all_data
                        if not self.is_screenshot or len(all_data) == 0:
                            all_data.append(sub_cd)
                        else:
                            # current step is screenshot, we have to judge current is first or not
                            last_data = all_data[-1]
                            if last_data.test_action.lower() == 'screenshot' and not sub_cd.step_desc:
                                # last step is screenshot, add current blocking data, then update it
                                last_data.append_ignore_blocks(blocking_data)
                                all_data[-1] = last_data
                            else:
                                # last step not screenshot, just add it to all_data
                                sub_cd.append_ignore_blocks(blocking_data)
                                all_data.append(sub_cd)
            except Exception:
                ex_str = traceback.format_exc()
                print("Error is :{}".format(ex_str))
            return all_data
        return None

    def get_cell_value(self, col_index, row_index, sheet):
        field_type = sheet.cell(rowx=row_index, colx=col_index).ctype
        # number
        if field_type == 2:
            value = convert_value(sheet.cell(rowx=row_index, colx=col_index).value)
        else:
            value = str(sheet.cell(rowx=row_index, colx=col_index).value)
        return value

    def get_case_data(self):
        if self.path:
            all_data = []
            sheet = self.get_sheet(self.path, self.sheet_name)
            header_dict = {}
            try:
                for row_index in range(sheet.nrows):
                    cd = CaseData()
                    row_current = []
                    for col_index in range(sheet.ncols):
                        value = self.get_cell_value(col_index, row_index, sheet)
                        if row_index == 0:
                            header_dict[col_index] = value
                        else:
                            row_current.append(value)
                            if header_dict[col_index] == 'id':
                                cd.id = int(value)
                            elif header_dict[col_index] == 'test_name':
                                cd.test_name = value
                            elif header_dict[col_index] == 'test_priority':
                                cd.test_priority = value
                            elif header_dict[col_index] == 'steps':
                                cd.steps = get_list(value)
                            elif header_dict[col_index] == 'author':
                                cd.author = value
                            elif header_dict[col_index] == 'test_inherit':
                                cd.test_inherit = get_list(value)

                    if row_index != 0 and cd.test_priority in ['P0', 'P1', 'P2']:
                        all_data.append(cd)
            except Exception:
                ex_str = traceback.format_exc()
                print("Error is :{}".format(ex_str))

            return all_data
        return None

    def get_sheet(self, path, sheet_name):
        excel = xlrd.open_workbook(path)
        sheet = excel.sheet_by_name(sheet_name)  # Open the sheet
        return sheet


def convert_value(old_value):
    if isinstance(old_value, float):
        old_value = [str(old_value), int(old_value)][int(old_value) == old_value]
        return old_value
    else:
        return str(old_value)


def get_list(value):
    if value:
        return str(value).split('|')
    else:
        return ['']


def get_test_case(settings, path, case_files, case_id=None, is_inherit=False):
    case_list = []
    try:
        #print('enter get test case: {}'.format(path))
        sheet_name = 'test_case'
        helper = ExcelHelper(path, sheet_name)
        cases_id = settings.get_ini(constant.SECTION_TEST_INFO, constant.SECTION_TEST_INFO_CASE_IDS)
        casesid_list = cases_id.split('|')

        all_data_case = helper.get_case_data()
        #print('all data case before: {}'.format(all_data_case))
        sub_sheet_name = 'steps'
        helper = ExcelHelper(path, sub_sheet_name)
        all_data_sub_case = helper.get_sub_case_data()

        if cases_id and not is_inherit:
            all_data_case = list(filter(lambda x: str(x.id) in casesid_list, all_data_case))

        if case_id:
            case_id = int(case_id)
            all_data_case = list(filter(lambda x: x.id == case_id, all_data_case))

        #print('all data case: {}'.format(all_data_case))
        for data in all_data_case:
            #print('data case name: ', data.test_name)
            data.has_inherit = False
            if len(data.test_inherit) == 2:
                common_path = data.test_inherit[0]
                common_case = data.test_inherit[1]
                #print('common path: {}'.format(common_path))
                #print('common case: {}'.format(common_case))
                inherit_case = common_path + '.xlsx'
                if inherit_case in case_files.keys():
                    #print('case in case files')
                    data.has_inherit = True
                    case_list = case_list + get_test_case(settings, case_files[inherit_case], case_files, int(common_case), is_inherit=True)
                    #print('case list size: {}'.format(len(case_list)))
            steps = [int(x) for x in data.steps if x != '']
            sub_case_step = []
            for step in steps:
                filter_list = list(filter(lambda sub_data: int(sub_data.step_id) == step, all_data_sub_case))
                if len(filter_list) > 0:
                    sub_case_step.append(filter_list[0])

            data.steps = sub_case_step
            data.is_inherit = is_inherit
            case_list.append(data)
    except Exception as error:
        traceback.print_exc()
        print ("Excel Format Error", error)
        case_list = []

    return case_list

