#  Copyright: (c) 2023, Liudmila Sherstnyakova
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import datetime
import io
from typing import IO, Dict

import numpy as np

from nmbu.rinex.common import *
from nmbu.rinex.navigation.v3.nav_message_type.BDS import BDSNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.GAL import GALNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.GPS import GPSNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.IRN import IRNNavRecord
from nmbu.rinex.navigation.v3.nav_message_type.QZS import QZSNavRecord


class IONCorrections:
    pass

class NavigationHeaderV3:
    """
    Class that holds the result of parsing header from Navigation file in version 3.
    Contains following fields:

    - agency: str
    - created_by: str
    - creation_time: datetime
    - version: float
    - file_type: str
    - gnss: str
    - other: {str: str}
    """
    def __init__(self, version: float, file_type: str, gnss: str):
        self.agency: str = ""
        self.created_by: str = ""
        self.creation_time: datetime = None
        self.version: float = version
        self.file_type: str = file_type
        self.gnss: str = gnss
        self.corrections: Dict[str, Dict[str, Dict[str, IONCorrections]]] = {
            'ION': {}
        }
        self.other: Dict[str, str] = {}


def read_navigation_header_v3(
        file: IO,
        version: float,
        file_type: str,
        gnss: str
) -> NavigationHeaderV3:
    """
    Parses input file line by line until 'END OF HEADER' line is read.
    All header lines are extracted and parsed according to Rinex V3 specification for Navigation header

    :param file: file iterator. Supposed to start at line number 2, as the first line is read by reader.__read_first_line
    :param version: version of the file as read by reader.__read_first_line
    :param file_type: type of the file as read by reader.__read_first_line
    :param gnss: gnss of the file as read by reader.__read_first_line
    :return: NavigationHeaderV3 object filled with necessary data
    """
    result = NavigationHeaderV3(version, file_type, gnss)

    for line in file:
        if line.__contains__(END_OF_HEADER_LABEL):
            break

        if line.__contains__(PGM_RUNBY_DATE_LABEL):
            result.created_by = line[:20].strip()
            result.agency = line[20:40].strip()
            result.creation_time = datetime.strptime(line[40:60].strip(), "%Y%m%d %H%M%S %Z")
        elif line.__contains__(IONOSPHERIC_CORR_LABEL):
            gnss = line[:3]
            sv_no = line[56:58].strip()
            time_mark = line[54].strip() if line[54].strip() != '' else 'NO_TIME'
            corr_type = line[3]
            if gnss == 'GAL':
                sv_name = GALNavRecord.gnss_symbol + sv_no
                values = np.genfromtxt(io.BytesIO(line[5:54].encode("ascii")),
                              delimiter=(12,)*4,
                              dtype=GALNavRecord.ion_corr_line_format)

                result.corrections['ION'][sv_name] = {time_mark: IONCorrections()}

                result.corrections['ION'][sv_name][time_mark].ai0 = values['ai0']
                result.corrections['ION'][sv_name][time_mark].ai1 = values['ai1']
                result.corrections['ION'][sv_name][time_mark].ai2 = values['ai2']
                result.corrections['ION'][sv_name][time_mark].ai3 = values['ai3']
            elif gnss in ('BDS', 'GPS', 'QZS', 'IRN') and corr_type == 'A':
                if gnss == 'BDS':
                    sv_name = BDSNavRecord.gnss_symbol + sv_no
                elif gnss == 'GPS':
                    sv_name = GPSNavRecord.gnss_symbol + sv_no
                elif gnss == 'QZS':
                    sv_name = QZSNavRecord.gnss_symbol + sv_no
                else:
                    sv_name = IRNNavRecord.gnss_symbol + sv_no

                values = np.genfromtxt(io.BytesIO(line[5:54].encode("ascii")),
                                       delimiter=(12,) * 4,
                                       dtype=np.dtype([
                                           ('alpha0', np.float64), ('alpha1', np.float64),
                                           ('alpha2', np.float64), ('alpha3', np.float64)
                                       ]))
                if sv_name not in result.corrections['ION'].keys():
                    result.corrections['ION'][sv_name] = {}
                if time_mark not in result.corrections['ION'][sv_name].keys():
                    result.corrections['ION'][sv_name][time_mark] = IONCorrections()

                result.corrections['ION'][sv_name][time_mark].Alpha0 = values['alpha0']
                result.corrections['ION'][sv_name][time_mark].Alpha1 = values['alpha1']
                result.corrections['ION'][sv_name][time_mark].Alpha2 = values['alpha2']
                result.corrections['ION'][sv_name][time_mark].Alpha3 = values['alpha3']

            elif gnss in ('BDS', 'GPS', 'QZS', 'IRN') and corr_type == 'B':
                if gnss == 'BDS':
                    sv_name = BDSNavRecord.gnss_symbol + sv_no
                elif gnss == 'GPS':
                    sv_name = GPSNavRecord.gnss_symbol + sv_no
                elif gnss == 'QZS':
                    sv_name = QZSNavRecord.gnss_symbol + sv_no
                else:
                    sv_name = IRNNavRecord.gnss_symbol + sv_no

                values = np.genfromtxt(io.BytesIO(line[5:54].encode("ascii")),
                                       delimiter=(12,) * 4,
                                       dtype=np.dtype([
                                           ('beta0', np.float64), ('beta1', np.float64),
                                           ('beta2', np.float64), ('beta3', np.float64)
                                       ]))
                if sv_name not in result.corrections['ION'].keys():
                    result.corrections['ION'][sv_name] = {}
                if time_mark not in result.corrections['ION'][sv_name].keys():
                    result.corrections['ION'][sv_name][time_mark] = IONCorrections()

                result.corrections['ION'][sv_name][time_mark].Beta0 = values['beta0']
                result.corrections['ION'][sv_name][time_mark].Beta1 = values['beta1']
                result.corrections['ION'][sv_name][time_mark].Beta2 = values['beta2']
                result.corrections['ION'][sv_name][time_mark].Beta3 = values['beta3']
            else:
                print("Unknown gnss for {l:s}: {gnss:s}{corr_type:s}".format(
                    l=IONOSPHERIC_CORR_LABEL,
                    gnss=gnss, corr_type=corr_type))
        else:
            label = line[60:80].strip()
            if label in result.other.keys():
                result.other[label] += " | " + line[:60].strip()
            else:
                result.other[label] = line[:60].strip()
        # end of for loop

    return result
