# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 10:11:05 2018

@author: mmilkovits

Abstract Base Class for data storage format

"""

import abc
import pandas as pd

class Database(abc.ABC):
    
    """ Abstract Base Class for EMAT data storage
    
    Database constains the design experiments, meta-model parameters, 
    and the core and meta-model results (performance measures)
    """

    def get_db_info(self):
        """
        Get a short string describing this Database

        Returns:
            str
        """
        return "no info available"

    @abc.abstractmethod
    def init_xlm(self, parameter_list, measure_list):
        """
        Initialize or extend set of experiment variables and measures
        
        Initialize database with universe of risk variables, 
        policy variables, and performance measures. All variables and measures
        defined in scopes must be defined in this set.
        This method only needs to be run
        once after creating a new database.

        Args:
            parameter_list (List[tuple]): Experiment variable tuples
                (variable name, type)
                where variable name is a string and
                type is 'uncertainty', 'lever', or 'constant'
            measure_list (List[tuple]): Performance measure tuples
                (performance measure name, type)
                where type is 'regional', 'transit', 'corridor', etc.
                See scope yaml file for all categories

        """   
    
    @abc.abstractmethod
    def write_scope(self, scope_name, sheet, scp_xl, scp_m, content):
        """Save the emat scope information to the database
          
        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            sheet (str): yaml file name with scope definition
            scp_m (List[str]): scope variables - risk variables and 
                strategy variables
            m_list (List[str]): scope performance measures
            content (Scope): scope object
        Raises:
            KeyError: If scope name already exists, the scp_vars are not
                available, or the performance measures are not initialized
                in the database.
        
        """     

    @abc.abstractmethod
    def read_scope(self, scope_name):
        """Load the pickled scope from the database.

        Args:
            scope_name (str): scope name

        Returns:
            Scope
        """

    @abc.abstractmethod
    def add_scope_meas(self, scope_name, scp_m):
        """Update the set of performance measures associated with the scope
        
        Use this function when the core model runs are complete to add
        performance measures to the scope and post-process against the 
        archived results
          
        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            scp_m (List[str]): scope performance measures
        Raises:
            KeyError: If scope name does not exist or the 
                performance measures are not initialized in the database.
        
        """     
    
    @abc.abstractmethod
    def delete_scope(self, scope_name):
        """Delete the scope from the database
        
        Deletes the scope as well as any experiments and results associated
        with the scope
        
        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run"""  
        
    @abc.abstractmethod
    def write_experiment_parameters(self, scope_name, design_name, xl_df):
        """Write experiment definitions
        
        Records values for each experiment variable per experiment
        
        
        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            design_name (str): experiment design type:
                'uni' - generated by univariate sensitivity test design
                'lhs' - generated by latin hypercube sample design
            xl_df (pandas Dataframe): columns are experiment variables, 
                each row is a full experiment

        Returns:
            list: the experiment id's of the newly recorded experiments

        Raises:
            UserWarning: If scope name does not exist
            TypeError: If not all scope variables are defined in the 
                exp_def
        """     

    def write_experiment_parameters_1(self, scope_name, design_name: str, *args, **kwargs):
        """Write experiment definitions for a single experiment.

        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            design_name (str): experiment design name.
            parameters (dict): keys are experiment parameters, values are the
                experimental values to look up.  Subsequent positional or keyword
                arguments are used to update parameters.

        Returns:
            list: the experiment id's of the newly recorded experiments

        Raises:
            UserWarning: If scope name does not exist
            TypeError: If not all scope variables are defined in the
                exp_def
        """
        parameters = {}
        for a in args:
            parameters.update(a)
        parameters.update(kwargs)
        xl_df = pd.DataFrame(parameters, index=[0])
        result = self.write_experiment_parameters(scope_name, design_name, xl_df)
        return result[0]


    @abc.abstractmethod
    def read_experiment_parameters(self, scope_name, design=None, only_pending=False):
        """Read experiment definitions
        
        Read the values from each experiment variable per experiment
        
        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            design (str, optional): If given, only experiments associated
                with the named design are returned, otherwise all
                experiments are returned.
            only_pending (bool, default False): If True, only pending
                experiments (which have no performance measure results
                stored in the database) are returned.

        Returns:
            pandas.DataFrame: experiment definitions

        Raises:
            ValueError: if `scope_name` is not stored in this database
        """    

    @abc.abstractmethod
    def write_experiment_measures(self, scope_name, source, m_df):
        """Write experiment results  
        
        Write the performance measure results for each experiment 
        in the scope - if the scope does not exist, nothing is recorded
        
        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            cm_src (int): indicator of performance measure source
                (0 = core model or non-zero = meta-model id)
            m_df (pandas Dataframe): columns are the performance
                measure names, row indexes are the experiment id
        Raises:
            UserWarning: If scope name does not exist        
        """         

    @abc.abstractmethod
    def read_experiment_all(
            self,
            scope_name,
            design_name,
            source=None,
            only_pending=False,
            ensure_dtypes=False,
    ):
        """Read experiment definitions and results
        
        Read the values from each experiment variable and the 
        results for each performance measure per experiment
        
        Args:
            scope_name (str): scope name, used to identify experiments
                including uncertainties, policy levers, and
                performance measures associated with this run.
            design (str or Collection[str]): experimental design name (a
                single str) or a collection of design names to read.
            source (int, optional): The source identifier of the
                experimental outcomes to load.  If not given, but
                there are only results from a single source in the
                database, those results are returned.  If there are
                results from multiple sources, an error is raised.
            only_pending (bool, default False): If True, only pending
                experiments (which have no performance measure results
                stored in the database) are returned.
            ensure_dtypes (bool, default False): If True, the scope
                associated with these experiments is also read out
                of the database, and that scope file is used to
                format experimental data consistently (i.e., as
                float, integer, bool, or categorical).
        Returns:
            experiment (pandas.DataFrame): experiment definition and 
                performance measures
        Raises:
            ValueError
                When no source is given but the database contains
                results from multiple sources.
        """

    @abc.abstractmethod
    def read_experiment_measures(
            self,
            scope_name,
            design,
            experiment_id=None,
            source=None,
    ):
        """Read experiment results

        Read the
        results for each performance measure per experiment

        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            design (str): experiment design type:
                'uni' - generated by univariate sensitivity test design
                'lhs' - generated by latin hypercube sample design
            experiment_id (int, optional): The id of the experiment to
                retrieve.  If omitted, get all experiments matching the
                scope and design.
            source (int, optional): The source identifier of the
                experimental outcomes to load.  If not given, but
                there are only results from a single source in the
                database, those results are returned.  If there are
                results from multiple sources, an error is raised.
        Returns:
            results (pandas.DataFrame): performance measures
        Raises:
            ValueError
                When no source is given but the database contains
                results from multiple sources.
        """

    @abc.abstractmethod
    def delete_experiments(self, scope_name, design):
        """Delete experiment definitions and results
        
        Deletes all records from an experiment design
        
        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            design (str): experiment design type:
                'uni' - generated by univariate sensitivity test design
                'lhs' - generated by latin hypercube sample design
        """
        
    @abc.abstractmethod
    def write_experiment_all(self, scope_name, design, source, xlm_df):
        """Write experiment definitions and results
        
        Writes the values from each experiment variable and the 
        results for each performance measure per experiment
        
        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            design (str): experiment design type:
                'uni' - generated by univariate sensitivity test design
                'lhs' - generated by latin hypercube sample design
            source (int): indicator of performance measure source
                (0 = core model or non-zero = meta-model id)
            xlm_df (pandas.Dataframe): columns are the experiment
                variables and measure names
        Raises:
            UserWarning: If scope and design already exist 
            TypeError: If not all scope variables are defined in the 
                experiment
        """     


    @abc.abstractmethod
    def read_scope_names(self, design_name=None) -> list:
        """A list of all available scopes in the database.

        Args:
            design_name (str, optional): If a design name, is given, only
                scopes containing a design with this name are returned.

        Returns:
            list
        """

    @abc.abstractmethod
    def read_design_names(self, scope_name:str) -> list:
        """A list of all available designs for a given scope.

        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
        """

    @abc.abstractmethod
    def read_experiment_ids(self, scope_name:str, design_name:str, xl_df) -> list:
        """Read the experiment ids previously defined in the database

        Args:
            scope_name (str): scope name, used to identify experiments,
                performance measures, and results associated with this run
            design_name (str or None): experiment design name.  Set to None
                to find experiments across all designs.
            xl_df (pandas.DataFrame): columns are experiment parameters,
                each row is a full experiment

        Returns:
            list: the experiment id's of the identified experiments

        Raises:
            ValueError: If scope name does not exist
            ValueError: If multiple experiments match an experiment definition.
                This can happen, for example, if the definition is incomplete.
        """


    @abc.abstractmethod
    def read_uncertainties(self, scope_name:str) -> list:
        """A list of all uncertainties for a given scope.

        Args:
            scope_name (str): scope name
        """

    @abc.abstractmethod
    def read_levers(self, scope_name:str) -> list:
        """A list of all levers for a given scope.

        Args:
            scope_name (str): scope name
        """

    @abc.abstractmethod
    def read_constants(self, scope_name:str) -> list:
        """A list of all constants for a given scope.

        Args:
            scope_name (str): scope name
        """

    @abc.abstractmethod
    def read_measures(self, scope_name:str) -> list:
        """A list of all performance measures for a given scope.

        Args:
            scope_name (str): scope name
        """

    @abc.abstractmethod
    def write_metamodel(self, scope_name, metamodel, metamodel_id=None, metamodel_name=''):
        """Store a meta-model in the database

         Args:
            scope_name (str): scope name
            metamodel (emat.MetaModel): The meta-model to be stored.
                If a PythonCoreModel containing a MetaModel is given,
                the MetaModel will be extracted.
            metamodel_id (int, optional): A unique id number for this
                metamodel.  If no id number is given and it cannot be
                inferred from `metamodel`, a unique id number
                will be created.
            metamodel_name (str, optional): A name for this meta-model.
                If no name is given and it cannot be
                inferred from `metamodel`, an empty string is used.
       """


    @abc.abstractmethod
    def read_metamodel(self, scope_name, metamodel_id=None):
        """Retrieve a meta-model from the database.

        Args:
            scope_name (str): scope name
            metamodel_id (int, optional): A unique id number for this
                metamodel.  If not given but there is exactly one
                metamodel stored for the given scope, that metamodel
                will be returned.

        Returns:
            PythonCoreModel: The meta-model, ready to use
        """

    @abc.abstractmethod
    def read_metamodel_ids(self, scope_name):
        """A list of all metamodel id's for a given scope.

        Args:
            scope_name (str): scope name
        """

    @abc.abstractmethod
    def get_new_metamodel_id(self, scope_name):
        """Get a new unused metamodel id for a given scope.

        Args:
            scope_name (str): scope name

        Returns:
            int
        """

    @abc.abstractmethod
    def read_box(self, scope_name: str, box_name: str, scope=None):
        """
        Read a Box from the database.

        Args:
            scope_name (str):
                The name of the scope from which to read the box.
            box_name (str):
                The name of the box to read.
            scope (Scope, optional):
                The Scope to assign to the Box that is returned.
                If not given, no Scope object is assigned to the
                box.

        Returns:
            Box
        """

    @abc.abstractmethod
    def read_box_names(self, scope_name: str):
        """
        Get the names of all boxes associated with a particular scope.

        Args:
            scope_name (str):
                The name of the scope from which to read the Box names.

        Returns:
            list[str]
        """

    @abc.abstractmethod
    def read_box_parent_name(self, scope_name: str, box_name:str):
        """
        Get the name of the parent box for a particular box in the database

        Args:
            scope_name (str):
                The name of the scope from which to read the Box parent.
            box_name (str):
                The name of the box from which to read the parent.

        Returns:
            str or None:
                If the identified box has a parent, this is the name of that
                parent, otherwise None is returned.

        """

    @abc.abstractmethod
    def read_box_parent_names(self, scope_name: str):
        """
        Get the name of the parent box for each box in the database.

        Args:
            scope_name (str):
                The name of the scope from which to read Box parents.

        Returns:
            dict
                A dictionary, with keys giving Box names and values
                giving the respective Box parent names.

        """

    @abc.abstractmethod
    def read_boxes(self, scope_name: str=None, scope=None):
        """
        Read Boxes from the database.

        Args:
            scope_name (str, optional):
                The name of the scope from which to load Boxes. This
                is used exclusively to identify the Boxes to load from
                the database, and the scope by this name is not attached
                to the Boxes, unless `scope` is given, in which case this
                argument is ignored.
            scope (Scope, optional):
                The scope to assign to the Boxes.  If not given,
                no Scope object is assigned.

        Returns:
            Boxes
        """

    @abc.abstractmethod
    def write_box(self, box, scope_name=None):
        """
        Write a single box to the database.

        Args:
            box (Box):
                The Box to write to the database.
            scope_name (str, optional):
                The scope name to use when writing to the database. If
                the `boxes` has a particular scope assigned, the name
                of that scope is used.

        Raises:
            ValueError:
                If the `box` has a particular scope assigned, and
                `scope_name` is given but it is not the same name
                of the assigned scope.

        """

    @abc.abstractmethod
    def write_boxes(self, boxes, scope_name=None):
        """
        Write Boxes to the database.

        Args:
            boxes (Boxes):
                The collection of Boxes to write to the database.
            scope_name (str, optional):
                The scope name to use when writing to the database. If
                the `boxes` has a particular scope assigned, the name
                of that scope is used.

        Raises:
            ValueError:
                If the `boxes` has a particular scope assigned, and
                `scope_name` is given but it is not the same name
                of the assigned scope.

        """
