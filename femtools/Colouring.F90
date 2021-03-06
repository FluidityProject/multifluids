!    Copyright (C) 2006 Imperial College London and others.
!    
!    Please see the AUTHORS file in the main source directory for a full list
!    of copyright holders.
!
!    Prof. C Pain
!    Applied Modelling and Computation Group
!    Department of Earth Science and Engineering
!    Imperial College London
!
!    amcgsoftware@imperial.ac.uk
!    
!    This library is free software; you can redistribute it and/or
!    modify it under the terms of the GNU Lesser General Public
!    License as published by the Free Software Foundation,
!    version 2.1 of the License.
!
!    This library is distributed in the hope that it will be useful,
!    but WITHOUT ANY WARRANTY; without even the implied warranty of
!    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
!    Lesser General Public License for more details.
!
!    You should have received a copy of the GNU Lesser General Public
!    License along with this library; if not, write to the Free Software
!    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
!    USA
#include "fdebug.h"

module colouring
  use fields
  use fields_manipulation
  use fields_base
  use data_structures
  use sparse_tools
  implicit none

  public :: colour_sparsity, verify_colour_sparsity, verify_colour_ispsparsity
  public :: colour_sets
  
contains
  


  ! Converts the matrix sparsity to an isp sparsity which can then be coloured to reduce the number 
  ! of function evaluations needed to compute a (sparse) Jacobian via differencing.
  ! This function returns S^T*S if S is the given sparsity matrix.
  ! The resulting sparsity matrix is symmetric. 
  function mat_sparsity_to_isp_sparsity(sparsity_in) result(sparsity_out)
    type(csr_sparsity), intent(in) :: sparsity_in
    type(csr_sparsity) :: sparsity_out
    type(csr_sparsity) :: sparsity_in_T

    sparsity_in_T=transpose(sparsity_in)
    sparsity_out=matmul(sparsity_in_T, sparsity_in)
    call deallocate(sparsity_in_T)

  end function mat_sparsity_to_isp_sparsity 



  ! This routine colours a graph using the greedy approach. 
  ! It takes as argument the sparsity of the adjacency matrix of the graph 
  ! (i.e. the matrix is node X nodes and symmetric for undirected graphs).
  subroutine colour_sparsity(sparsity, mesh, node_colour, no_colours)
    type(csr_sparsity), intent(in) :: sparsity    
    type(mesh_type), intent(inout) :: mesh
    type(scalar_field), intent(out) :: node_colour
    integer, intent(out) :: no_colours

    integer, dimension(:), pointer:: cols
    type(integer_set) :: neigh_colours
    integer :: i, node

    call allocate(node_colour, mesh, "NodeColouring")

    ! Set the first node colour
    call set(node_colour, 1, 1.0)
    no_colours = 1

    ! Colour remaining nodes.
    do node=2, size(sparsity,1)
       call allocate(neigh_colours)
       ! Determine colour of neighbours.
       cols => row_m_ptr(sparsity, node)
       do i=1, size(cols)
          if(cols(i)<node) then
            call insert(neigh_colours, nint(node_val(node_colour,cols(i))))
          end if
       end do

       ! Find the lowest unused colour in neighbourhood.
       do i=1, no_colours+1
          if(.not.has_value(neigh_colours, i)) then
             call set(node_colour, node, float(i))
             if(i>no_colours) then
                no_colours = i
             end if
             exit
          end if
       end do
       call deallocate(neigh_colours)
    end do
    
  end subroutine colour_sparsity

  ! Checks if a sparsity colouring is valid. 
  function verify_colour_sparsity(sparsity, node_colour) result(valid)
    type(csr_sparsity), intent(in) :: sparsity
    type(scalar_field), intent(in) :: node_colour
    logical :: valid
    integer :: i, node 
    real :: my_colour
    integer, dimension(:), pointer:: cols
  
    valid=.true. 
    do node=1, size(sparsity, 1)
      cols => row_m_ptr(sparsity, node)
      my_colour=node_val(node_colour, node)
      ! Each nonzero column is a neighbour of node, so lets make sure that they do not have the same colour.
      do i=1, size(cols)
        if (cols(i)<node .and. my_colour==node_val(node_colour, cols(i))) then
          valid=.false.
        end if
      end do
    end do
  end function verify_colour_sparsity

  ! Checks if a sparsity colouring of a matrix is valid for isp.
  ! This method checks that no two columns of the same colour have 
  ! nonzeros at the same positions. 
  function verify_colour_ispsparsity(mat_sparsity, node_colour) result(valid)
    type(csr_sparsity), intent(in) :: mat_sparsity
    type(scalar_field), intent(in) :: node_colour
    logical :: valid
    integer :: i, row 
    integer, dimension(:), pointer:: cols
    type(integer_set) :: neigh_colours
  
    valid=.true. 
    do row=1, size(mat_sparsity, 1)
      call allocate(neigh_colours)
      cols => row_m_ptr(mat_sparsity, row)
      do i=1, size(cols)
        if (has_value(neigh_colours, nint(node_val(node_colour, cols(i))))) then
          valid=.false.
        end if
        call insert(neigh_colours, nint(node_val(node_colour,cols(i))))
      end do
      call deallocate(neigh_colours)
    end do
  end function verify_colour_ispsparsity

  ! with above colour_sparsity, we get map:node_id --> colour
  ! now we want map: colour --> node_ids 
  function colour_sets(sparsity, node_colour, no_colours) result(clr_sets)
    type(csr_sparsity), intent(in) :: sparsity    
    type(scalar_field), intent(in) :: node_colour
    integer, intent(in) :: no_colours
    type(integer_set), dimension(no_colours) :: clr_sets
    integer :: node

    call allocate(clr_sets)
    do node=1, size(sparsity, 1)
       call insert(clr_sets(nint(node_val(node_colour, node))), node)
    end do

  end function colour_sets

end module colouring
